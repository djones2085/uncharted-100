#!/usr/bin/env python3
"""
The Uncharted 100: A Critical Audiophile Companion to Front-to-Back Masterpieces
Compilation and Publication Engine

This script:
1. Verifies and downloads high-resolution cover art (from iTunes Search API and canonical master archives).
2. Compiles uncharted_100_companion.md (complete, publication-grade Markdown discovery guide).
3. Compiles uncharted_100_companion.html (luxury digital companion book with responsive typography and artwork).
4. Renders uncharted_100_companion.pdf (print-ready PDF book rendered via Headless Chrome).
"""

import os
import sys
import json
import urllib.request
import urllib.parse
import ssl
import subprocess
import time
import base64
import re

# Import the 8 taxonomy data modules
from data.cat1_analog_soul import CAT1_ALBUMS
from data.cat2_dream_pop import CAT2_ALBUMS
from data.cat3_dynamic_rock import CAT3_ALBUMS
from data.cat4_cinematic_hiphop import CAT4_ALBUMS
from data.cat5_acoustic_roots import CAT5_ALBUMS
from data.cat6_avant_pop import CAT6_ALBUMS
from data.cat7_nocturnal_electronics import CAT7_ALBUMS
from data.cat8_transcendental_sacred import CAT8_ALBUMS
from data.category_sound_profiles import CATEGORY_SOUND_PROFILES

CATEGORIES = [
    {
        "num": "I",
        "title": "Analog Soul, Pocket & Organic Funk",
        "count": 15,
        "aesthetic": "2-inch tape tracking, unquantized human swing, vintage Neve/API console preamps, round sub-frequencies, close-mic vocal isolation.",
        "sound_profile": CATEGORY_SOUND_PROFILES["I"],
        "albums": CAT1_ALBUMS
    },
    {
        "num": "II",
        "title": "Jangle, Dream-Pop & Lyrical Intimacy",
        "count": 14,
        "aesthetic": "Rickenbacker/Fender chime, lush chorus modulation, ribbon-mic room air, ethereal vocal layers, melancholic chord geometry.",
        "sound_profile": CATEGORY_SOUND_PROFILES["II"],
        "albums": CAT2_ALBUMS
    },
    {
        "num": "III",
        "title": "Dynamic Rock, Texture & Kinetic Tension",
        "count": 13,
        "aesthetic": "Natural soundstage headroom, uncompressed room drums, sudden quiet-to-explosive transient attacks, analog tape saturation.",
        "sound_profile": CATEGORY_SOUND_PROFILES["III"],
        "albums": CAT3_ALBUMS
    },
    {
        "num": "IV",
        "title": "Cinematic Hip-Hop, Golden-Era Jazz & Conscious Narrative",
        "count": 14,
        "aesthetic": "Warm upright bass, crisp vinyl crackle, SP-1200/MPC60 quantization, cinematic horn arrangements, continuous three-act concept arcs.",
        "sound_profile": CATEGORY_SOUND_PROFILES["IV"],
        "albums": CAT4_ALBUMS
    },
    {
        "num": "V",
        "title": "Acoustic Roots, Room Ambience & Confessional Songwriting",
        "count": 14,
        "aesthetic": "Stereo ribbon mic pairs, vintage acoustic woods, mechanical pedal squeaks, zero artificial pitch correction, raw vocal proximity.",
        "sound_profile": CATEGORY_SOUND_PROFILES["V"],
        "albums": CAT5_ALBUMS
    },
    {
        "num": "VI",
        "title": "Avant-Pop, Baroque Grandeur & High-Art Synthesis",
        "count": 14,
        "aesthetic": "Architectural pacing, Fairlight CMI / analog synths, orchestral counterpoint, dynamic vocal gymnastics, bold thematic world-building.",
        "sound_profile": CATEGORY_SOUND_PROFILES["VI"],
        "albums": CAT6_ALBUMS
    },
    {
        "num": "VII",
        "title": "Nocturnal Electronics, Sub-Bass & Trip-Hop Spatiality",
        "count": 8,
        "aesthetic": "Dub echo decays, pitch-shifted vinyl lacquers, subterranean sub-bass extension, tape flutter, dark room staging.",
        "sound_profile": CATEGORY_SOUND_PROFILES["VII"],
        "albums": CAT7_ALBUMS
    },
    {
        "num": "VIII",
        "title": "Transcendental Sacred, Chamber Hymns & Spiritual Contemplation",
        "count": 8,
        "aesthetic": "Pipe organ overtones, liturgical acoustic staging, reverent quietude, close acoustic guitars, multi-part vocal hymns.",
        "sound_profile": CATEGORY_SOUND_PROFILES["VIII"],
        "albums": CAT8_ALBUMS
    }
]

ALL_ALBUMS = []
for cat in CATEGORIES:
    ALL_ALBUMS.extend(cat["albums"])


def ensure_covers_downloaded():
    """Ensures all 100 covers are downloaded and cataloged in covers_manifest.json."""
    os.makedirs("covers", exist_ok=True)
    manifest = {}
    if os.path.exists("covers_manifest.json"):
        try:
            with open("covers_manifest.json", "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    ssl_ctx = ssl._create_unverified_context()
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=ssl_ctx))
    urllib.request.install_opener(opener)

    updated = False
    for alb in ALL_ALBUMS:
        aid_str = str(alb["id"])
        local_fp = manifest.get(aid_str, {}).get("local_path")
        
        # If not in manifest or file missing / tiny, re-download
        if not local_fp or not os.path.exists(local_fp) or os.path.getsize(local_fp) < 5000:
            target_fn = f"covers/{alb['id']:03d}_{alb['artist']}_{alb['album']}.jpg".replace(" ", "_").replace("/", "_").replace("'", "").replace("&", "and").replace("?", "").replace("!", "").replace(":", "")
            art_url = alb.get("web_art_url")
            print(f"[{alb['id']:03d}/100] Fetching artwork for: {alb['artist']} - {alb['album']}...")
            try:
                req = urllib.request.Request(art_url, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'})
                with urllib.request.urlopen(req, timeout=15) as resp, open(target_fn, "wb") as out_f:
                    out_f.write(resp.read())
                
                manifest[aid_str] = {
                    "id": alb["id"],
                    "artist": alb["artist"],
                    "album": alb["album"],
                    "artwork_url": art_url,
                    "local_path": target_fn
                }
                updated = True
                time.sleep(0.2)
            except Exception as e:
                print(f"Error downloading cover for {alb['album']}: {e}")

    if updated or not os.path.exists("covers_manifest.json"):
        with open("covers_manifest.json", "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    # Sync local paths into album objects
    for alb in ALL_ALBUMS:
        aid_str = str(alb["id"])
        if aid_str in manifest:
            alb["local_cover"] = manifest[aid_str]["local_path"]
            alb["web_cover"] = manifest[aid_str]["artwork_url"]
        else:
            alb["local_cover"] = alb["cover_file"]
            alb["web_cover"] = alb["web_art_url"]


def generate_markdown():
    """Generates the publication-grade Markdown guide."""
    lines = []
    
    # -------------------------------------------------------------------------
    # BOOK COVER PAGE & FRONTISPIECE
    # -------------------------------------------------------------------------
    lines.append("# ==============================================================================")
    lines.append("#                 THE UNCHARTED 100: AUDIOPHILE COMPANION BOOK")
    lines.append("# ==============================================================================")
    lines.append("#")
    lines.append("#       THE CRITICAL AUDIOPHILE COMPANION TO FRONT-TO-BACK MASTERPIECES")
    lines.append("#               One Hundred Front-to-Back Studio Masterclasses")
    lines.append("#           Strictly Uncollected in the Listener's Apple Music Archive")
    lines.append("#")
    lines.append("#                         Volume I | Autumn 2026")
    lines.append("#")
    lines.append("# ------------------------------------------------------------------------------")
    lines.append("# CURATORIAL DIRECTIVE: Zero-Overlap Library Compliance Guaranteed")
    lines.append("# ACOUSTIC STANDARDS:   Dynamic Range DR11+, 2-Inch Tape, Unquantized Timing,")
    lines.append("#                       Ribbon Mics, Three-Dimensional Soundstaging")
    lines.append("# FOLIO IMPRINT:        The High-Fidelity Listening Society | Private Archive")
    lines.append("# ==============================================================================\n")

    lines.append("> *\"The long-playing record is an acoustic cathedral. When you walk inside, you do not admire a single stained glass pane and leave; you inhabit the space until the light has traveled from dawn to midnight.\"*\n")
    lines.append("> — **Curatorial Prolegomena Epigraph**\n")
    lines.append("---\n")

    # Distinctive Opening Section: Curator's Inscription
    lines.append("## The Curator's Inscription: The Sanctity of the Full-Length Ritual\n")
    lines.append(
        "You hold in your hands (and on your screen) a compendium designed for an endangered species of music lover: "
        "**the dedicated front-to-back album listener**. In a digital music economy engineered to atomize our attention spans "
        "into thirty-second dopamine bursts, randomized algorithmic queues, and hyper-compressed background filler, "
        "committing sixty uninterrupted minutes to a single artistic vision is an act of quiet defiance.\n\n"
        "The one hundred albums assembled across these eight taxonomies represent front-to-back recording art in its purest form. "
        "Every selection has been vetted under an absolute negative filter against your existing Apple Music library: "
        "there is zero overlap, zero re-hash, and zero filler. Yet every record speaks fluently to the tonal DNA you already revere—from "
        "the velvet tape intimacy of Norah Jones and Mac Miller to the shimmering guitar jangle of The Sundays, the raw dynamic fire "
        "of Nirvana's *MTV Unplugged*, and the cathedral stillness of Audrey Assad.\n\n"
        "Treat each entry not as an isolated recommendation, but as an acoustic destination. Before dropping the needle on any album herein, "
        "absorb the **Acoustic Archetype & Sound Profile** at the head of each category. Calibrate your listening environment. Power down distractions. "
        "Inhabit the room.\n"
    )
    lines.append("---\n")

    # Introduction & Critical Manifesto
    lines.append("## Prolegomena: The Lost Architecture of the Full-Length Masterpiece\n")
    lines.append(
        "In the contemporary streaming landscape, music consumption has been atomized into thirty-second algorithmic snippets, "
        "curated mood playlists, and compressed background wallpaper. Yet the long-playing album (LP) remains humanity's greatest "
        "recording art form: an intentional, uninterrupted thirty-to-eighty minute architecture where dynamic pacing, narrative resolution, "
        "and acoustic engineering converge into a singular emotional journey.\n\n"
        "This companion guide is designed specifically for an active, discerning listener who refuses the shuffle button, values organic soundstaging, "
        "analog tape saturation, natural transient snap, and three-dimensional vocal proximity. Every one of the 100 albums selected herein "
        "has been meticulously vetted to ensure **strict, absolute zero-overlap** with the listener's existing library, while systematically "
        "expanding upon the tonal DNA of their most cherished records (from the acoustic hush of Norah Jones and Mac Miller to the shimmering "
        "jangle of The Sundays, the unvarnished electricity of Nirvana's *MTV Unplugged*, and the sacred stillness of Audrey Assad).\n"
    )

    # Taxonomy Overview
    lines.append("## The 8 Audiophile Sonic Taxonomies\n")
    lines.append("| Category | Taxonomy Name | Album Count | Primary Sonic & Aesthetic Signature |")
    lines.append("| :--- | :--- | :---: | :--- |")
    for cat in CATEGORIES:
        lines.append(f"| **Category {cat['num']}** | {cat['title']} | {cat['count']} | {cat['aesthetic']} |")
    lines.append("\n---\n")

    # Master Roster Quick-Index
    lines.append("## Complete 100-Album Master Roster\n")
    for cat in CATEGORIES:
        lines.append(f"### Category {cat['num']}: {cat['title']} ({cat['count']} Albums)")
        for alb in cat["albums"]:
            lines.append(f"- **#{alb['id']:03d}** {alb['artist']} – *{alb['album']}* ({alb['year']})")
        lines.append("")
    lines.append("---\n")

    # The 100 Deep Critical Entries with Category Sound Profiles
    for cat in CATEGORIES:
        lines.append(f"# Category {cat['num']}: {cat['title']}\n")
        lines.append(f"> **Sonic Signature:** *{cat['aesthetic']}*\n\n")

        # Distinctive Section Opening: The Sound of This Category
        prof = cat["sound_profile"]
        lines.append(f"## The Sound of Category {cat['num']}: {prof['sound_title']}\n")
        lines.append(f"> *\"{prof['sound_summary']}\"*\n\n")
        lines.append("### Acoustic Archetype & Engineering Philosophy")
        lines.append(f"{prof['engineering_philosophy']}\n")
        lines.append("### Frequency Architecture & Spectral Balance")
        lines.append(f"{prof['frequency_architecture']}\n")
        lines.append("### Spatial Soundstaging & Holographic Imaging")
        lines.append(f"{prof['spatial_soundstaging']}\n")
        lines.append("### The Tactile Listening Experience")
        lines.append(f"{prof['tactile_listening_experience']}\n")
        lines.append("---\n\n")

        for alb in cat["albums"]:
            lines.append(f"## {alb['id']}. {alb['artist']} – *{alb['album']}* ({alb['year']})\n")
            lines.append(f"**Primary Label & Engineering:** `{alb['label_engineer']}`\n\n")
            
            # Embed image with local relative path and direct high-res link
            lines.append(f"![{alb['artist']} - {alb['album']}]({alb['local_cover']})\n\n")
            lines.append(f"*High-Resolution Master Artwork Archive:* [{alb['album']} Cover Art]({alb['web_cover']})\n\n")

            lines.append("### Curatorial Justification (Why It's on This List)")
            lines.append(f"{alb['curatorial_justification']}\n")

            lines.append("### Front-to-Back Architecture (Narrative & Pacing)")
            lines.append(f"{alb['front_to_back_architecture']}\n")

            lines.append("### Audiophile & Production Breakdown")
            lines.append(f"{alb['audiophile_breakdown']}\n")

            lines.append(f"### Benchmark Demo Track: **\"{alb['benchmark_demo_track']}\"**")
            lines.append(f"{alb['benchmark_demo_analysis']}\n")

            lines.append("### Tonal Anchor Bridge (Library Connection)")
            lines.append(f"{alb['tonal_anchor_bridge']}\n")

            lines.append("---\n")

    # Appendices
    lines.append("# Appendices & Reference Materials\n")
    lines.append("## Appendix A: Audiophile Calibration & Listening Room Optimization Guide\n")
    lines.append(
        "To experience these 100 masterpieces with maximum fidelity, adhere to the following acoustic guidelines:\n\n"
        "1. **The Equilateral Listening Triangle:** For loudspeaker setups, position your primary listening chair at the apex of "
        "an exact equilateral triangle formed with the acoustic centers of your left and right monitor tweeters. Angle (toe-in) each "
        "speaker so the tweeters aim directly at your ears, minimizing early sidewall reflections.\n"
        "2. **Subwoofer Crossover & Phase Integration:** Set your active subwoofer low-pass filter between 60Hz and 80Hz, matching the natural "
        "bass roll-off of your main drivers. Adjust continuous phase control while playing Category I (e.g., D'Angelo's *Black Messiah*) "
        "or Category VII (Massive Attack's *Mezzanine*) until the low-end reaches peak tactile impact without boomy frequency cancelation.\n"
        "3. **Planar Magnetic & Headphone Headroom:** When listening via open-back planar magnetic headphones, utilize a dedicated high-current "
        "discrete headphone amplifier. Planar drivers demand pure electrical current to control transient attack on explosive percussion tracks "
        "(e.g., Radiohead's 'Reckoner' or The Breeders' 'Cannonball') without transient compression or distortion.\n"
        "4. **Room Damping & First Reflection Treatment:** Treat early lateral reflection points on side walls with 2-inch to 4-inch "
        "rigid fiberglass or rockwool acoustic panels. This preserves the holographic soundstage imaging and pin-point instrument localization "
        "crucial for chamber folk (Category V: Gillian Welch) and liturgical hymns (Category VIII: The Brilliance).\n"
    )

    lines.append("## Appendix B: Cross-Reference Matrix (Library Loved Records -> Uncharted 100)\n")
    lines.append("| Loved Library Record | Uncharted 100 Bridge Album | Primary Shared Audiophile & Tonal Dimension |")
    lines.append("| :--- | :--- | :--- |")
    lines.append("| **The Sundays** – *Reading, Writing and Arithmetic* | **Cocteau Twins** – *Heaven or Las Vegas* (#016) | Chorus-drenched shimmering guitar chime & ethereal melodic vocals |")
    lines.append("| **The Sundays** – *Static & Silence* | **Real Estate** – *Days* (#026) | Fender clean tone warmth, Twin Reverb spring decay, pastoral jangle |")
    lines.append("| **Mac Miller** – *Circles* | **Adrianne Lenker** – *songs* (#023) | Unfiltered whisper-track vocal intimacy, close-mic acoustic wood resonance |")
    lines.append("| **Mac Miller** – *Circles* | **Saba** – *CARE FOR ME* (#047) | Intimate acoustic piano chords, live jazz pocket, vulnerable confessional grief |")
    lines.append("| **Nirvana** – *MTV Unplugged in New York* | **Gillian Welch** – *Time (The Revelator)* (#057) | Raw live room acoustic tracking, zero pitch correction, physical dynamic presence |")
    lines.append("| **Nirvana** – *MTV Unplugged in New York* | **Jeff Buckley** – *Grace* (#032) | Catastrophic vocal dynamic range, transcendent emotional release, raw telecaster chime |")
    lines.append("| **Norah Jones** – *Come Away With Me* | **Cleo Sol** – *Mother* (#004) | Sacred living-room intimacy, warm upright bass, gentle nylon-string picking |")
    lines.append("| **Norah Jones** – *Come Away With Me* | **Julia Jacklin** – *Crushing* (#068) | Unhurried vocal phrasing, authentic wooden room decay, heartbreak clarity |")
    lines.append("| **Lauryn Hill** – *The Miseducation of Lauryn Hill* | **Erykah Badu** – *Mama's Gun* (#002) | Electric Lady 2-inch tape tracking, Soulquarian live groove, brass warmth |")
    lines.append("| **Lauryn Hill** – *The Miseducation of Lauryn Hill* | **The Roots** – *Things Fall Apart* (#043) | Unquantized live hip-hop breakbeats, conscious street poetry, Bob Power mixing |")
    lines.append("| **Amy Winehouse** – *Back to Black* | **Snoh Aalegra** – *Ugh, those feels again* (#012) | Velvet smoky alto vocals, sweeping orchestral strings, Motown/Stax nostalgia |")
    lines.append("| **Amy Winehouse** – *Back to Black* | **Portishead** – *Dummy* (#086) | Dusty vinyl crackle, mournful Rhodes keys, torch-song heartbreak |")
    lines.append("| **Cannons** – *Fever Dream* | **Sade** – *Love Deluxe* (#003) | Sultry, spacious basslines, nocturnal minimalism, silky vocal delivery |")
    lines.append("| **Cannons** – *Fever Dream* | **The xx** – *xx* (#088) | Pitch-black soundstage silence, clean guitar delay, subterranean 808 sub-bass |")
    lines.append("| **Kacey Musgraves** – *Golden Hour* | **Big Thief** – *Dragon New Warm Mountain...* (#019) | Modern organic folk warmth, inventive acoustic textures, cosmic love poetry |")
    lines.append("| **Kacey Musgraves** – *Golden Hour* | **Sierra Ferrell** – *Trail of Flowers* (#065) | Gary Paczosa acoustic string staging, bell-like mountain vocal brilliance |")
    lines.append("| **Audrey Assad** – *Inheritance* | **The Brilliance** – *Brother* (#094) | Sacred liturgical chamber strings, Steinway grand piano, reverent quietude |")
    lines.append("| **Audrey Assad** – *Inheritance* | **All Sons & Daughters** – *Poets & Saints* (#100) | Historic European church acoustics, pipe organ overtones, intimate dual vocal harmony |")
    lines.append("| **Hillsong UNITED** – *Empires* | **Citizens** – *A Thousand Shores* (#097) | Sweeping dream-pop synth pads, soaring alternative rock guitars, expansive soundstage |")
    lines.append("| **Hillsong UNITED** – *Empires* | **Josh Garrels** – *Love & War & The Sea In Between* (#099) | Epic cinematic orchestral folk, multi-octave falsetto hymns, spiritual pilgrimage |")
    lines.append("| **Kendrick Lamar** – *DAMN.* | **GZA** – *Liquid Swords* (#045) | Dark, cinematic narrative sequencing, 12-bit sample grit, philosophical discipline |")
    lines.append("| **Kendrick Lamar** – *DAMN.* | **D'Angelo and The Vanguard** – *Black Messiah* (#001) | Uncompromising analog tape tracking, visceral sociopolitical fervor, virtuoso pocket |")
    lines.append("| **SZA** – *Ctrl* | **Jazmine Sullivan** – *Heaux Tales* (#021) | Conversational vocal vulnerability, spoken-word interludes, virtuosic vocal runs |")
    lines.append("| **SZA** – *Ctrl* | **Noname** – *Room 25* (#049) | Intimate live jazz trio, rapid conversational cadence, unapologetic feminine honesty |")
    lines.append("| **Billie Eilish** – *HIT ME HARD AND SOFT* | **Elliott Smith** – *Either/Or* (#033) | Double-tracked whispered vocal proximity, unadorned acoustic fingerpicking |")
    lines.append("| **Billie Eilish** – *HIT ME HARD AND SOFT* | **Björk** – *Homogenic* (#072) | Sudden tectonic electronic sub-bass eruptions colliding with acoustic strings |")
    lines.append("| **Lorde** – *Melodrama* | **Kate Bush** – *Hounds of Love* (#071) | Theatrical avant-pop ambition, conceptual two-act architecture, soaring vocal art |")
    lines.append("| **Lorde** – *Melodrama* | **Robyn** – *Body Talk* (#078) | Crying-in-the-club synthesizer pop perfection, cathartic electronic beats |")
    lines.append("| **Chappell Roan** – *The Rise and Fall of a Midwest Princess* | **Caroline Polachek** – *Desire, I Want to Turn Into You* (#075) | Operatic vocal gymnastics, exuberant pop surrealism, Mediterranean acoustic flair |")
    lines.append("| **Chappell Roan** – *The Rise and Fall of a Midwest Princess* | **Camera Obscura** – *Let's Get Out of This Country* (#028) | Baroque orchestral melodrama, witty romantic lyricism, chiming 60s pop hooks |")
    lines.append("| **Paramore** – *After Laughter* | **Alvvays** – *Blue Rev* (#018) | Kinetic 12-string guitar jangle, sardonic lyrical wit, uncompressed dynamic punch |")
    lines.append("| **No Doubt** – *Tragic Kingdom* | **The Breeders** – *Last Splash* (#041) | Playful irreverence, thunderous quiet-loud bass riffs, infectious pop-rock hooks |")
    lines.append("| **Adele** – *21* | **Brandi Carlile** – *By the Way, I Forgive You* (#061) | Room-shaking chest voice power, raw acoustic heartbreak, string quartet warmth |")
    lines.append("| **Ella Langley** – *Dandelion* | **Lucinda Williams** – *Car Wheels on a Gravel Road* (#059) | Southern backroad poetry, biting telecaster slide guitars, whiskey-tinged grit |")
    lines.append("| **Forrest Frank** – *CHILD OF GOD* | **Liz Vice** – *There's a Light* (#096) | Joyous, organic gospel-soul brass, infectious rhythm, redemptive spiritual light |")

    return "\n".join(lines)


def generate_html():
    """Generates the publication-grade HTML digital companion book."""
    html_parts = []
    html_parts.append("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Uncharted 100: A Critical Audiophile Companion to Front-to-Back Masterpieces</title>
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Uncharted 100">
  <meta name="theme-color" content="#0a0c10">
  <link rel="apple-touch-icon" href="apple-touch-icon.png">
  <style>
    :root {
      --bg-deep: #0a0c10;
      --bg-surface: #12151c;
      --bg-card: #181d26;
      --bg-card-hover: #1e2430;
      --border: #262d3d;
      --gold: #d4af37;
      --gold-light: #f3e5ab;
      --gold-dim: #997d25;
      --text-main: #e2e8f0;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --accent-blue: #38bdf8;
      --accent-purple: #c084fc;
      --font-serif: "Charter", "Georgia", "Iowan Old Style", "Times New Roman", serif;
      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
      --font-mono: "SF Mono", Menlo, Monaco, Consolas, monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      background-color: var(--bg-deep);
      color: var(--text-main);
      font-family: var(--font-sans);
      line-height: 1.65;
      font-size: 16px;
      -webkit-font-smoothing: antialiased;
    }

    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 0 24px;
    }

    /* Dedicated Book Cover Page Styles */
    .book-cover-page {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 60px 24px;
      background: radial-gradient(circle at 50% 35%, #151a24 0%, #07090d 100%);
      border-bottom: 2px solid var(--gold-dim);
      page-break-after: always;
      break-after: page;
    }

    .cover-filigree-border {
      width: 100%;
      max-width: 980px;
      border: 2px solid var(--gold);
      outline: 1px solid var(--gold-dim);
      outline-offset: -12px;
      padding: 60px 48px;
      background: rgba(14, 17, 24, 0.95);
      box-shadow: 0 25px 60px rgba(0, 0, 0, 0.8), inset 0 0 40px rgba(212, 175, 55, 0.05);
      position: relative;
    }

    .cover-inner-content {
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 32px;
    }

    .cover-top-matter {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
    }

    .cover-series-crest {
      display: flex;
      align-items: center;
      gap: 16px;
      width: 100%;
      max-width: 680px;
    }

    .crest-line {
      flex: 1;
      height: 1px;
      background: linear-gradient(90deg, transparent, var(--gold-dim), var(--gold), var(--gold-dim), transparent);
    }

    .crest-text {
      font-family: var(--font-mono);
      font-size: 0.8rem;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--gold-light);
      white-space: nowrap;
    }

    .cover-edition-badge {
      font-family: var(--font-mono);
      font-size: 0.72rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--text-dim);
      margin-top: 4px;
    }

    .cover-center-matter {
      display: flex;
      flex-direction: column;
      align-items: center;
      max-width: 840px;
    }

    .cover-ornament {
      color: var(--gold);
      font-size: 1.1rem;
      letter-spacing: 0.3em;
      margin-bottom: 16px;
    }

    .cover-title-main {
      font-family: var(--font-serif);
      font-size: clamp(2.8rem, 6vw, 4.8rem);
      font-weight: 700;
      color: #ffffff;
      letter-spacing: 0.08em;
      line-height: 1.1;
      text-transform: uppercase;
      margin-bottom: 12px;
      text-shadow: 0 2px 10px rgba(0, 0, 0, 0.6);
    }

    .cover-title-separator {
      width: 120px;
      height: 2px;
      background: var(--gold);
      margin: 16px auto 20px;
    }

    .cover-title-sub {
      font-family: var(--font-serif);
      font-size: clamp(1.2rem, 2.5vw, 1.6rem);
      color: var(--gold-light);
      font-style: italic;
      margin-bottom: 16px;
      letter-spacing: 0.02em;
    }

    .cover-title-description {
      font-size: 0.95rem;
      color: var(--text-muted);
      line-height: 1.7;
      max-width: 660px;
      margin: 0 auto 24px;
    }

    .cover-emblem {
      margin: 8px 0 16px;
    }

    .cover-bottom-matter {
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 24px;
      border-top: 1px solid rgba(212, 175, 55, 0.25);
      padding-top: 28px;
    }

    .cover-manifesto-quote {
      font-family: var(--font-serif);
      font-style: italic;
      color: var(--gold-light);
      font-size: 0.95rem;
      max-width: 720px;
      line-height: 1.6;
    }

    .cover-colophon-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
      width: 100%;
      max-width: 880px;
      margin-top: 8px;
    }

    .colophon-item {
      text-align: center;
      padding: 10px;
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border);
      border-radius: 6px;
    }

    .colophon-label {
      font-family: var(--font-mono);
      font-size: 0.68rem;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--gold-dim);
      margin-bottom: 4px;
    }

    .colophon-val {
      font-size: 0.8rem;
      color: var(--text-main);
      font-weight: 500;
    }

    /* Hero Header */
    header.hero {
      padding: 80px 0 60px;
      background: radial-gradient(circle at 50% 20%, #1c2230 0%, var(--bg-deep) 80%);
      border-bottom: 1px solid var(--border);
      text-align: center;
    }

    .hero-badge {
      display: inline-block;
      padding: 6px 16px;
      border: 1px solid var(--gold-dim);
      border-radius: 9999px;
      color: var(--gold-light);
      font-size: 0.85rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      font-family: var(--font-mono);
      margin-bottom: 24px;
      background: rgba(212, 175, 55, 0.08);
    }

    h1.hero-title {
      font-family: var(--font-serif);
      font-size: clamp(2.5rem, 5vw, 4rem);
      font-weight: 700;
      line-height: 1.15;
      color: #fff;
      margin-bottom: 16px;
      letter-spacing: -0.02em;
    }

    p.hero-subtitle {
      font-size: 1.25rem;
      color: var(--text-muted);
      max-width: 760px;
      margin: 0 auto 32px;
      font-weight: 300;
    }

    .hero-stats {
      display: flex;
      justify-content: center;
      gap: 32px;
      flex-wrap: wrap;
      margin-top: 32px;
    }

    .stat-pill {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      padding: 10px 20px;
      border-radius: 8px;
      font-family: var(--font-mono);
      font-size: 0.9rem;
    }
    .stat-pill strong { color: var(--gold); }

    /* Sticky Navigation */
    nav.category-nav {
      position: sticky;
      top: 0;
      z-index: 100;
      background: rgba(10, 12, 16, 0.92);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 12px 0;
      overflow-x: auto;
      white-space: nowrap;
    }

    .nav-inner {
      display: flex;
      gap: 12px;
      padding: 0 24px;
      max-width: 1200px;
      margin: 0 auto;
    }

    .nav-btn {
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.82rem;
      padding: 6px 14px;
      border-radius: 6px;
      background: var(--bg-surface);
      border: 1px solid var(--border);
      transition: all 0.2s ease;
      font-family: var(--font-mono);
    }
    .nav-btn:hover {
      background: var(--bg-card);
      color: var(--gold-light);
      border-color: var(--gold-dim);
    }

    /* Manifesto Section */
    section.manifesto {
      padding: 60px 0;
      border-bottom: 1px solid var(--border);
    }

    .manifesto-box {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 40px;
      border-left: 4px solid var(--gold);
    }

    .manifesto-box h2 {
      font-family: var(--font-serif);
      font-size: 1.8rem;
      color: #fff;
      margin-bottom: 16px;
    }

    .manifesto-box p {
      font-size: 1.05rem;
      color: var(--text-muted);
      margin-bottom: 16px;
    }

    /* Curator's Inscription */
    section.curator-inscription-section {
      padding: 60px 0 20px;
    }

    .curator-inscription-card {
      background: linear-gradient(145deg, #161b24 0%, #10131a 100%);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 44px;
      border-left: 4px solid var(--gold);
      box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    }

    .inscription-badge {
      font-family: var(--font-mono);
      font-size: 0.8rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--gold);
      margin-bottom: 12px;
    }

    .inscription-title {
      font-family: var(--font-serif);
      font-size: 1.85rem;
      color: #fff;
      margin-bottom: 16px;
    }

    .inscription-body p {
      font-size: 1.05rem;
      color: var(--text-muted);
      margin-bottom: 16px;
      line-height: 1.7;
    }
    .inscription-body p:last-child {
      margin-bottom: 0;
    }

    /* Category Section */
    section.category-block {
      padding: 80px 0 40px;
    }

    .category-header {
      margin-bottom: 36px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 24px;
    }

    .category-number {
      font-family: var(--font-mono);
      color: var(--gold);
      font-size: 0.9rem;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      margin-bottom: 8px;
    }

    .category-title {
      font-family: var(--font-serif);
      font-size: 2.4rem;
      color: #fff;
      margin-bottom: 12px;
    }

    .category-aesthetic {
      font-size: 1.1rem;
      color: var(--text-muted);
      font-style: italic;
    }

    /* Category Sound Profile Showcase */
    .category-sound-showcase {
      background: linear-gradient(140deg, #151a24 0%, #10131b 100%);
      border: 1px solid rgba(212, 175, 55, 0.35);
      border-left: 4px solid var(--gold);
      border-radius: 16px;
      padding: 36px;
      margin-bottom: 54px;
      box-shadow: 0 12px 36px rgba(0,0,0,0.5);
    }

    .sound-showcase-header {
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      padding-bottom: 20px;
      margin-bottom: 24px;
    }

    .sound-tag {
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 0.75rem;
      letter-spacing: 0.15em;
      text-transform: uppercase;
      color: var(--gold-light);
      background: rgba(212, 175, 55, 0.12);
      border: 1px solid var(--gold-dim);
      padding: 4px 12px;
      border-radius: 9999px;
      margin-bottom: 12px;
    }

    .sound-showcase-title {
      font-family: var(--font-serif);
      font-size: 1.75rem;
      color: #fff;
      margin-bottom: 10px;
      font-weight: 700;
    }

    .sound-showcase-summary {
      font-size: 1.1rem;
      color: var(--text-muted);
      font-style: italic;
      line-height: 1.6;
    }

    .sound-quad-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 24px;
    }

    .sound-card {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 22px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .sound-card-title {
      font-family: var(--font-mono);
      font-size: 0.82rem;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--gold);
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .sound-card p {
      font-size: 0.92rem;
      color: var(--text-muted);
      line-height: 1.65;
    }

    /* Album Card */
    .album-card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 16px;
      margin-bottom: 60px;
      padding: 36px;
      display: grid;
      grid-template-columns: 320px 1fr;
      gap: 36px;
      transition: transform 0.2s ease, border-color 0.2s ease;
      page-break-inside: avoid;
    }

    .album-card:hover {
      border-color: rgba(212, 175, 55, 0.4);
      transform: translateY(-2px);
    }

    .card-media {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 12px;
    }

    .cover-frame {
      width: 100%;
      aspect-ratio: 1/1;
      border-radius: 12px;
      overflow: hidden;
      background: #000;
      border: 1px solid var(--border);
      box-shadow: 0 12px 30px rgba(0,0,0,0.6);
      position: relative;
    }

    .cover-frame img {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
      transition: transform 0.3s ease;
    }
    .cover-frame:hover img {
      transform: scale(1.03);
    }

    .album-badge-bar {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: 8px;
      width: 100%;
    }

    .badge-tag {
      background: var(--bg-surface);
      border: 1px solid var(--border);
      color: var(--gold-light);
      padding: 4px 10px;
      border-radius: 6px;
      font-size: 0.75rem;
      font-family: var(--font-mono);
    }

    .media-benchmarks {
      display: flex;
      flex-direction: column;
      gap: 12px;
      width: 100%;
      margin-top: 4px;
    }

    /* Card Content */
    .card-content {
      display: flex;
      flex-direction: column;
      gap: 20px;
    }

    .album-id-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      border-bottom: 1px solid rgba(255,255,255,0.08);
      padding-bottom: 12px;
    }

    .album-title-group h3 {
      font-family: var(--font-serif);
      font-size: 1.85rem;
      color: #fff;
      font-weight: 700;
      line-height: 1.2;
    }

    .album-title-group .artist-name {
      font-size: 1.25rem;
      color: var(--gold);
      margin-top: 4px;
      font-weight: 600;
    }

    .meta-index {
      font-family: var(--font-mono);
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-dim);
    }

    .label-spec {
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: var(--text-muted);
      background: var(--bg-surface);
      padding: 6px 12px;
      border-radius: 6px;
      border: 1px solid var(--border);
      display: inline-block;
    }

    .section-title {
      font-family: var(--font-sans);
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-dim);
      font-weight: 700;
      margin-bottom: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .section-title::before {
      content: "";
      display: inline-block;
      width: 4px;
      height: 12px;
      background: var(--gold);
      border-radius: 2px;
    }

    .analysis-text {
      color: var(--text-main);
      font-size: 0.96rem;
      line-height: 1.6;
    }

    .benchmark-box {
      background: rgba(56, 189, 248, 0.05);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: 10px;
      padding: 14px 16px;
    }
    .benchmark-box .benchmark-name {
      color: var(--accent-blue);
      font-weight: 700;
      font-family: var(--font-mono);
      font-size: 0.88rem;
      margin-bottom: 6px;
    }
    .benchmark-text {
      color: var(--text-muted);
      font-size: 0.85rem;
      line-height: 1.5;
    }

    .bridge-box {
      background: rgba(212, 175, 55, 0.06);
      border: 1px solid rgba(212, 175, 55, 0.25);
      border-radius: 10px;
      padding: 14px 16px;
    }
    .bridge-box .bridge-label {
      color: var(--gold-light);
      font-weight: 700;
      font-size: 0.80rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      font-family: var(--font-mono);
      margin-bottom: 4px;
    }
    .bridge-text {
      color: var(--text-muted);
      font-size: 0.85rem;
      line-height: 1.5;
    }

    .table-container {
      overflow-x: auto;
      margin: 32px 0;
      border: 1px solid var(--border);
      border-radius: 10px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
    }

    th, td {
      padding: 14px 18px;
      border-bottom: 1px solid var(--border);
    }

    th {
      background: var(--bg-surface);
      color: var(--gold-light);
      font-family: var(--font-mono);
      font-size: 0.8rem;
      letter-spacing: 0.05em;
      text-transform: uppercase;
    }

    tr:nth-child(even) { background: rgba(255,255,255,0.015); }
    tr:hover { background: rgba(212, 175, 55, 0.04); }

    footer {
      border-top: 1px solid var(--border);
      padding: 60px 0;
      text-align: center;
      color: var(--text-dim);
      font-size: 0.9rem;
      font-family: var(--font-mono);
    }

    @page {
      size: letter portrait;
      margin: 10mm 12mm;
    }

    @media print {
      body {
        background: #fff !important;
        color: #111 !important;
        margin: 0 !important;
        padding: 0 !important;
      }
      .category-nav, header.hero, footer { display: none !important; }

      /* Full-Bleed Book Cover Page */
      .book-cover-page {
        page-break-before: avoid !important;
        break-before: avoid !important;
        page-break-after: always !important;
        break-after: page !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        background: transparent !important;
        border: none !important;
        color: #fff !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        padding: 0 !important;
        margin: 0 !important;
        height: 100% !important;
        max-height: 100% !important;
        overflow: hidden !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }

      .cover-filigree-border {
        width: 100% !important;
        max-width: 660px !important;
        border: 2px solid #d4af37 !important;
        outline: 1px solid #997d25 !important;
        outline-offset: -8px !important;
        background: #0f1219 !important;
        box-sizing: border-box !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
        padding: 24px 24px !important;
        border-radius: 6px !important;
        box-shadow: none !important;
        -webkit-print-color-adjust: exact !important;
        print-color-adjust: exact !important;
      }

      .cover-inner-content {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        text-align: center !important;
        gap: 10px !important;
        width: 100% !important;
      }

      .cover-top-matter {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 4px !important;
      }

      .cover-series-crest {
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
        width: 100% !important;
        max-width: 540px !important;
      }

      .crest-line {
        flex: 1 !important;
        height: 1px !important;
        background: linear-gradient(90deg, transparent, #856a1e, #d4af37, #856a1e, transparent) !important;
      }

      .crest-text {
        font-family: var(--font-mono) !important;
        font-size: 0.68rem !important;
        letter-spacing: 0.16em !important;
        text-transform: uppercase !important;
        color: #e5c158 !important;
        white-space: nowrap !important;
      }

      .cover-edition-badge {
        font-family: var(--font-mono) !important;
        font-size: 0.62rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: #888 !important;
        margin-top: 2px !important;
      }

      .cover-center-matter {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        max-width: 600px !important;
      }

      .cover-ornament {
        color: #d4af37 !important;
        font-size: 0.9rem !important;
        letter-spacing: 0.25em !important;
        margin-bottom: 6px !important;
      }

      .cover-title-main {
        font-family: var(--font-serif) !important;
        font-size: 2.6rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        letter-spacing: 0.06em !important;
        line-height: 1.05 !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
        background: none !important;
        -webkit-background-clip: initial !important;
        -webkit-text-fill-color: #ffffff !important;
        text-shadow: none !important;
      }

      .cover-title-separator {
        width: 90px !important;
        height: 1.5px !important;
        background: #d4af37 !important;
        margin: 8px auto 10px !important;
      }

      .cover-title-sub {
        font-family: var(--font-serif) !important;
        font-size: 1.05rem !important;
        color: #e5c158 !important;
        font-style: italic !important;
        margin-bottom: 6px !important;
        letter-spacing: 0.02em !important;
      }

      .cover-title-description {
        font-size: 0.78rem !important;
        color: #94a3b8 !important;
        line-height: 1.4 !important;
        max-width: 520px !important;
        margin: 0 auto 8px !important;
      }

      .cover-emblem {
        margin: 4px 0 6px !important;
      }
      .cover-emblem svg {
        width: 68px !important;
        height: 68px !important;
      }

      .cover-bottom-matter {
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        gap: 8px !important;
        border-top: 1px solid rgba(212, 175, 55, 0.25) !important;
        padding-top: 10px !important;
      }

      .cover-manifesto-quote {
        font-family: var(--font-serif) !important;
        font-style: italic !important;
        color: #e5c158 !important;
        font-size: 0.76rem !important;
        max-width: 540px !important;
        line-height: 1.35 !important;
      }

      .cover-colophon-grid {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        max-width: 580px !important;
        margin-top: 2px !important;
      }

      .colophon-item {
        text-align: center !important;
        padding: 6px 8px !important;
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(212, 175, 55, 0.25) !important;
        border-radius: 4px !important;
      }

      .colophon-label {
        font-family: var(--font-mono) !important;
        font-size: 0.58rem !important;
        letter-spacing: 0.1em !important;
        text-transform: uppercase !important;
        color: #b8972e !important;
        margin-bottom: 2px !important;
      }

      .colophon-val {
        font-size: 0.68rem !important;
        color: #e2e8f0 !important;
        font-weight: 500 !important;
      }

      /* Interior Book Margins & Typography */
      main.container {
        max-width: 100% !important;
        width: 100% !important;
        padding: 0 !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
      }

      .curator-inscription-section, section.manifesto {
        page-break-after: always !important;
        break-after: page !important;
        color: #111 !important;
        background: #fff !important;
        padding: 6mm 0 10mm !important;
      }
      .curator-inscription-card, .manifesto-box {
        background: #fdfdfd !important;
        border: 1px solid #ddd !important;
        color: #111 !important;
        box-shadow: none !important;
        padding: 22px !important;
      }
      .inscription-title, .manifesto-box h2 {
        color: #000 !important;
      }
      .inscription-body p, .manifesto-box p {
        color: #333 !important;
      }

      .category-block {
        padding: 0 !important;
        margin: 0 !important;
      }
      .category-intro-page {
        page-break-before: always !important;
        break-before: page !important;
        page-break-after: always !important;
        break-after: page !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
      .category-header {
        border-bottom: 2px solid #222 !important;
        margin-bottom: 12px !important;
        padding-bottom: 8px !important;
      }
      .category-number {
        font-family: var(--font-mono) !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        color: #805b00 !important;
      }
      .category-title {
        font-family: var(--font-serif) !important;
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        color: #000 !important;
        margin: 3px 0 !important;
      }
      .category-aesthetic {
        font-size: 0.82rem !important;
        color: #475569 !important;
        font-style: italic !important;
      }

      .category-sound-showcase {
        page-break-after: always !important;
        break-after: page !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        background: #fbfbfb !important;
        border: 1px solid #dcdcdc !important;
        border-left: 4px solid #b8972e !important;
        border-radius: 10px !important;
        color: #111 !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 12px 14px !important;
      }
      .sound-showcase-header {
        border-bottom: 1px solid rgba(0, 0, 0, 0.1) !important;
        padding-bottom: 6px !important;
        margin-bottom: 8px !important;
      }
      .sound-tag {
        color: #222 !important;
        background: #eaeaea !important;
        border: 1px solid #ccc !important;
        font-family: var(--font-mono) !important;
        font-size: 0.65rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        margin-bottom: 4px !important;
      }
      .sound-showcase-title {
        font-family: var(--font-serif) !important;
        font-size: 1.10rem !important;
        font-weight: 700 !important;
        color: #000 !important;
        margin: 2px 0 3px !important;
      }
      .sound-showcase-summary {
        font-size: 0.78rem !important;
        color: #334155 !important;
        font-style: italic !important;
        line-height: 1.28 !important;
        margin-bottom: 6px !important;
      }
      .sound-quad-grid {
        display: grid !important;
        grid-template-columns: 1fr 1fr !important;
        gap: 10px !important;
      }
      .sound-card {
        background: #fff !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 6px !important;
        color: #222 !important;
        padding: 8px 10px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 4px !important;
      }
      .sound-card-title {
        color: #854d0e !important;
        font-weight: 700 !important;
        font-size: 0.72rem !important;
        font-family: var(--font-mono) !important;
        margin-bottom: 2px !important;
      }
      .sound-card p {
        color: #1e293b !important;
        font-size: 0.72rem !important;
        line-height: 1.30 !important;
        text-align: justify !important;
      }

      /* Album Card: Exactly One Page per Album */
      .album-card {
        display: grid !important;
        grid-template-columns: 215px 1fr !important;
        gap: 22px !important;
        page-break-before: always !important;
        break-before: page !important;
        page-break-inside: avoid !important;
        break-inside: avoid !important;
        page-break-after: always !important;
        break-after: page !important;
        border: 1px solid #dcdcdc !important;
        border-radius: 10px !important;
        background: #fff !important;
        color: #111 !important;
        box-shadow: none !important;
        margin: 0 !important;
        padding: 18px 20px !important;
      }
      .card-media {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 215px !important;
        gap: 10px !important;
      }
      .cover-frame {
        width: 215px !important;
        height: 215px !important;
        max-width: 215px !important;
        max-height: 215px !important;
        aspect-ratio: auto !important;
        border-radius: 8px !important;
        overflow: hidden !important;
        background: #f5f5f5 !important;
        border: 1px solid #d0d0d0 !important;
        box-shadow: none !important;
        margin: 0 !important;
      }
      .cover-frame img {
        width: 100% !important;
        height: 100% !important;
        display: block !important;
        object-fit: cover !important;
        margin: 0 !important;
        border: none !important;
      }
      .album-badge-bar {
        display: flex !important;
        flex-direction: row !important;
        justify-content: center !important;
        align-items: center !important;
        gap: 8px !important;
        width: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
      }
      .badge-tag {
        background: #f2f2f4 !important;
        border: 1px solid #d5d5d8 !important;
        color: #222 !important;
        font-family: var(--font-mono) !important;
        font-size: 0.72rem !important;
        font-weight: 600 !important;
        padding: 3px 8px !important;
        border-radius: 4px !important;
      }
      .media-benchmarks {
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
        width: 100% !important;
        margin-top: 4px !important;
      }
      .benchmark-box {
        background: #f7fafc !important;
        border: 1px solid #cbd5e1 !important;
        border-left: 3px solid #0284c7 !important;
        border-radius: 6px !important;
        padding: 8px 10px !important;
      }
      .benchmark-name {
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        color: #0369a1 !important;
        margin-bottom: 4px !important;
        line-height: 1.25 !important;
      }
      .benchmark-text {
        font-size: 0.73rem !important;
        line-height: 1.35 !important;
        color: #334155 !important;
      }
      .bridge-box {
        background: #fbf9f4 !important;
        border: 1px solid #e7dfc6 !important;
        border-left: 3px solid #b8972e !important;
        border-radius: 6px !important;
        padding: 8px 10px !important;
      }
      .bridge-label {
        font-family: var(--font-mono) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        color: #854d0e !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        margin-bottom: 4px !important;
      }
      .bridge-text {
        font-size: 0.73rem !important;
        line-height: 1.35 !important;
        color: #451a03 !important;
      }
      .card-content {
        display: flex !important;
        flex-direction: column !important;
        gap: 11px !important;
      }
      .album-id-header {
        display: flex !important;
        justify-content: space-between !important;
        align-items: baseline !important;
        border-bottom: 1.5px solid #222 !important;
        padding-bottom: 8px !important;
      }
      .album-title-group h3 {
        font-family: var(--font-serif) !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        color: #000 !important;
        line-height: 1.15 !important;
      }
      .album-title-group .artist-name {
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        color: #805b00 !important;
        margin-top: 3px !important;
      }
      .meta-index {
        font-family: var(--font-mono) !important;
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: #64748b !important;
      }
      .label-spec {
        font-family: var(--font-mono) !important;
        font-size: 0.75rem !important;
        color: #475569 !important;
        background: #f1f5f9 !important;
        border: 1px solid #e2e8f0 !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        display: inline-block !important;
      }
      .analysis-block {
        display: flex !important;
        flex-direction: column !important;
        gap: 3px !important;
      }
      .section-title {
        font-family: var(--font-sans) !important;
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        color: #0f172a !important;
        margin-bottom: 3px !important;
        display: flex !important;
        align-items: center !important;
        gap: 5px !important;
      }
      .section-title::before {
        content: "" !important;
        display: inline-block !important;
        width: 3px !important;
        height: 10px !important;
        background: #b8972e !important;
        border-radius: 1px !important;
      }
      .analysis-text {
        font-size: 0.80rem !important;
        line-height: 1.40 !important;
        color: #1e293b !important;
        text-align: justify !important;
      }

      /* Appendix Tables */
      .table-container {
        overflow-x: visible !important;
        margin: 20px 0 !important;
        border: 1px solid #ccc !important;
        page-break-inside: auto !important;
      }
      table {
        font-size: 0.82rem !important;
      }
      th {
        background: #f0f0f0 !important;
        color: #111 !important;
        border-bottom: 2px solid #999 !important;
      }
      td {
        border-bottom: 1px solid #ddd !important;
        color: #222 !important;
      }
      tr {
        page-break-inside: avoid !important;
        break-inside: avoid !important;
      }
    }

    @media screen and (max-width: 900px) {
      .sound-quad-grid {
        grid-template-columns: 1fr;
      }
      .cover-colophon-grid {
        grid-template-columns: 1fr 1fr;
      }
      .album-card {
        grid-template-columns: 1fr;
        gap: 24px;
      }
      .card-media {
        width: 100%;
        max-width: 280px;
        margin: 0 auto;
      }
      .cover-frame {
        width: 260px;
        height: 260px;
        max-width: 260px;
        max-height: 260px;
        margin: 0 auto 12px;
      }
      .album-badge-bar {
        justify-content: center;
      }
    }
  </style>
</head>
<body>

  <!-- Dedicated Book Cover Page (Page 1 in Print / Visual Gateway) -->
  <section class="book-cover-page" id="book-cover">
    <div class="cover-filigree-border">
      <div class="cover-inner-content">
        
        <div class="cover-top-matter">
          <div class="cover-series-crest">
            <span class="crest-line"></span>
            <span class="crest-text">CRITICAL AUDIOPHILE COMPANION SERIES • FOLIO NO. 1</span>
            <span class="crest-line"></span>
          </div>
          <div class="cover-edition-badge">AUTUMN 2026 ARCHIVAL CURATION • ZERO-OVERLAP CERTIFIED</div>
        </div>

        <div class="cover-center-matter">
          <div class="cover-ornament">✦ &nbsp; ❖ &nbsp; ✦</div>
          <h1 class="cover-title-main">THE UNCHARTED 100</h1>
          <div class="cover-title-separator"></div>
          <p class="cover-title-sub">A Critical Audiophile Companion to Front-to-Back Masterpieces</p>
          <p class="cover-title-description">
            One Hundred Essential Long-Playing Albums Strictly Uncollected in the Listener's Apple Music Archive, Curated Across Eight Sonic Taxonomies for the Discerning Full-Album Listener.
          </p>

          <!-- Audiophile Vinyl & Acoustic Waveform Emblem -->
          <div class="cover-emblem">
            <svg viewBox="0 0 120 120" width="100" height="100" class="emblem-svg">
              <circle cx="60" cy="60" r="56" fill="none" stroke="#d4af37" stroke-width="1.5" stroke-dasharray="4 2"/>
              <circle cx="60" cy="60" r="48" fill="none" stroke="rgba(212,175,55,0.4)" stroke-width="1"/>
              <circle cx="60" cy="60" r="40" fill="none" stroke="rgba(212,175,55,0.6)" stroke-width="1"/>
              <circle cx="60" cy="60" r="32" fill="none" stroke="rgba(212,175,55,0.3)" stroke-width="0.75"/>
              <circle cx="60" cy="60" r="22" fill="#181d26" stroke="#d4af37" stroke-width="1.5"/>
              <circle cx="60" cy="60" r="8" fill="#d4af37"/>
              <circle cx="60" cy="60" r="3" fill="#0a0c10"/>
              <line x1="10" y1="60" x2="30" y2="60" stroke="#d4af37" stroke-width="1"/>
              <line x1="90" y1="60" x2="110" y2="60" stroke="#d4af37" stroke-width="1"/>
              <line x1="60" y1="10" x2="60" y2="30" stroke="#d4af37" stroke-width="1"/>
              <line x1="60" y1="90" x2="60" y2="110" stroke="#d4af37" stroke-width="1"/>
            </svg>
          </div>
        </div>

        <div class="cover-bottom-matter">
          <div class="cover-manifesto-quote">
            “The long-playing record is an acoustic cathedral. When you walk inside, you do not admire a single stained glass pane and leave; you inhabit the space until the light has traveled from dawn to midnight.”
          </div>

          <div class="cover-colophon-grid">
            <div class="colophon-item">
              <div class="colophon-label">CURATORIAL MANDATE</div>
              <div class="colophon-val">100% Novelty / Library Excluded</div>
            </div>
            <div class="colophon-item">
              <div class="colophon-label">ACOUSTIC TAXONOMIES</div>
              <div class="colophon-val">8 Comprehensive Sound Realms</div>
            </div>
            <div class="colophon-item">
              <div class="colophon-label">PRODUCTION BENCHMARK</div>
              <div class="colophon-val">Master Tapes • DR11+ Headroom</div>
            </div>
            <div class="colophon-item">
              <div class="colophon-label">PRIVATE IMPRINT</div>
              <div class="colophon-val">High-Fidelity Listening Society</div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </section>

  <!-- Hero Header -->
  <header class="hero">
    <div class="container">
      <div class="hero-badge">Publication-Grade Critical Audiophile Edition</div>
      <h1 class="hero-title">The Uncharted 100</h1>
      <p class="hero-subtitle">
        A Critical Audiophile Companion to Front-to-Back Masterpieces | 100 Definitive Albums Strictly Uncollected in the Listener's Apple Music Library
      </p>
      <div class="hero-stats">
        <div class="stat-pill">Curated Roster: <strong>100 Albums</strong></div>
        <div class="stat-pill">Sonic Taxonomies: <strong>8 Distinct Categories</strong></div>
        <div class="stat-pill">Exclusion Overlap: <strong>0% (Strict Compliance)</strong></div>
        <div class="stat-pill">Audio Source: <strong>High-Resolution Master Tape & CD / Digital</strong></div>
      </div>
    </div>
  </header>

  <!-- Sticky Category Navigation -->
  <nav class="category-nav">
    <div class="nav-inner">
      <a href="#cat-I" class="nav-btn">I. Analog Soul & Funk</a>
      <a href="#cat-II" class="nav-btn">II. Jangle & Dream-Pop</a>
      <a href="#cat-III" class="nav-btn">III. Dynamic Rock</a>
      <a href="#cat-IV" class="nav-btn">IV. Cinematic Hip-Hop</a>
      <a href="#cat-V" class="nav-btn">V. Acoustic Roots</a>
      <a href="#cat-VI" class="nav-btn">VI. Avant-Pop & Baroque</a>
      <a href="#cat-VII" class="nav-btn">VII. Nocturnal Electronics</a>
      <a href="#cat-VIII" class="nav-btn">VIII. Transcendental Sacred</a>
      <a href="#calibration" class="nav-btn">Room Calibration</a>
      <a href="#matrix" class="nav-btn">Tonal Bridge Matrix</a>
    </div>
  </nav>

  <main class="container">

    <!-- Curator's Inscription / Distinctive Opening Section -->
    <section class="curator-inscription-section">
      <div class="curator-inscription-card">
        <div class="inscription-badge">Curator's Inscription • The Sacred Listening Ritual</div>
        <h2 class="inscription-title">The Needle on the Run-Out Groove: An Invitation to Pure Listening</h2>
        <div class="inscription-body">
          <p>
            You hold in your hands (and on your screen) a compendium designed for an endangered species of music lover: 
            <strong>the dedicated front-to-back album listener</strong>. In a digital music economy engineered to atomize our attention spans 
            into thirty-second dopamine bursts, randomized algorithmic queues, and hyper-compressed background filler, 
            committing sixty uninterrupted minutes to a single artistic vision is an act of quiet defiance.
          </p>
          <p>
            The one hundred albums assembled across these eight taxonomies represent front-to-back recording art in its purest form. 
            Every selection has been vetted under an absolute negative filter against your existing Apple Music library: 
            there is zero overlap, zero re-hash, and zero filler. Yet every record speaks fluently to the tonal DNA you already revere—from 
            the velvet tape intimacy of Norah Jones and Mac Miller to the shimmering guitar jangle of The Sundays, the raw dynamic fire 
            of Nirvana's <em>MTV Unplugged</em>, and the cathedral stillness of Audrey Assad.
          </p>
          <p>
            Treat each entry not as an isolated recommendation, but as an acoustic destination. Before dropping the needle on any album herein, 
            absorb the <em>Acoustic Archetype & Sound Profile</em> at the head of each category. Calibrate your listening environment. Power down distractions. 
            Inhabit the room.
          </p>
        </div>
      </div>
    </section>

    <!-- Prolegomena -->
    <section class="manifesto">
      <div class="manifesto-box">
        <h2>Prolegomena: The Lost Architecture of the Long-Playing Masterpiece</h2>
        <p>
          In an era dominated by micro-targeted streaming algorithms and atomized thirty-second playlists, the dedicated full-album 
          listener engages in a radical act of cultural and acoustic reverence. An authentic masterpiece is not a random grab-bag of 
          singles; it is a meticulously engineered sonic architecture where track sequencing, dynamic crests, acoustic decays, and 
          thematic resolutions are designed to be consumed as an uninterrupted emotional journey.
        </p>
        <p>
          This companion guide exists to expand the active listening frontiers of an audiophile who already possesses an extensive, 
          sophisticated Apple Music collection. Every one of the 100 albums profiled below has been rigorously cross-referenced against 
          the listener's library to ensure <strong>complete, zero-overlap novelty</strong>. Whether tracking D'Angelo's unquantized 
          two-inch tape groove through vintage Neve preamps, experiencing Elizabeth Fraser's multi-layered vocal heights in a three-dimensional 
          soundstage, or marveling at the quiet, uncompressed cabin acoustics of Adrianne Lenker, each entry stands as an undeniable masterclass 
          in front-to-back record-making.
        </p>
      </div>
    </section>
""")

    # Render Categories & Albums
    for cat in CATEGORIES:
        prof = cat["sound_profile"]
        html_parts.append(f"""
    <!-- Category {cat['num']} -->
    <section class="category-block" id="cat-{cat['num']}">
      <div class="category-intro-page">
        <div class="category-header">
          <div class="category-number">Category {cat['num']} • {cat['count']} Albums</div>
          <h2 class="category-title">{cat['title']}</h2>
          <div class="category-aesthetic">{cat['aesthetic']}</div>
        </div>

        <!-- Category Sound Profile Showcase -->
        <div class="category-sound-showcase">
          <div class="sound-showcase-header">
            <span class="sound-tag">Acoustic Archetype & Sound Profile</span>
            <h3 class="sound-showcase-title">{prof['sound_title']}</h3>
            <p class="sound-showcase-summary">“{prof['sound_summary']}”</p>
          </div>

          <div class="sound-quad-grid">
            <div class="sound-card">
              <div class="sound-card-title">🎛️ Engineering & Signal Chain</div>
              <p>{prof['engineering_philosophy']}</p>
            </div>

            <div class="sound-card">
              <div class="sound-card-title">📊 Frequency Architecture & Balance</div>
              <p>{prof['frequency_architecture']}</p>
            </div>

            <div class="sound-card">
              <div class="sound-card-title">🎧 Spatial Soundstaging & Depth</div>
              <p>{prof['spatial_soundstaging']}</p>
            </div>

            <div class="sound-card">
              <div class="sound-card-title">⚡ Tactile Listening Experience</div>
              <p>{prof['tactile_listening_experience']}</p>
            </div>
          </div>
        </div>
      </div>
""")

        for alb in cat["albums"]:
            html_parts.append(f"""
      <!-- Album Card #{alb['id']} -->
      <article class="album-card" id="album-{alb['id']}">
        <div class="card-media">
          <div class="cover-frame">
            <img src="{alb['local_cover']}" onerror="this.onerror=null; this.src='{alb['web_cover']}';" alt="{alb['artist']} - {alb['album']}" loading="lazy" />
          </div>
          <div class="album-badge-bar">
            <span class="badge-tag">#{alb['id']:03d} of 100</span>
            <span class="badge-tag">{alb['year']}</span>
          </div>
          <div class="media-benchmarks">
            <div class="benchmark-box">
              <div class="benchmark-name">Benchmark Demo: "{alb['benchmark_demo_track']}"</div>
              <p class="benchmark-text">{alb['benchmark_demo_analysis']}</p>
            </div>
            <div class="bridge-box">
              <div class="bridge-label">Tonal Anchor Bridge</div>
              <p class="bridge-text">{alb['tonal_anchor_bridge']}</p>
            </div>
          </div>
        </div>

        <div class="card-content">
          <div class="album-id-header">
            <div class="album-title-group">
              <h3>{alb['album']}</h3>
              <div class="artist-name">{alb['artist']}</div>
            </div>
            <div class="meta-index">#{alb['id']:03d}</div>
          </div>

          <div class="label-spec">
            <strong>Label / Engineering:</strong> {alb['label_engineer']}
          </div>

          <div class="analysis-block">
            <div class="section-title">Curatorial Justification (Why It's On This List)</div>
            <p class="analysis-text">{alb['curatorial_justification']}</p>
          </div>

          <div class="analysis-block">
            <div class="section-title">Front-to-Back Architecture (Narrative & Pacing)</div>
            <p class="analysis-text">{alb['front_to_back_architecture']}</p>
          </div>

          <div class="analysis-block">
            <div class="section-title">Audiophile & Production Breakdown</div>
            <p class="analysis-text">{alb['audiophile_breakdown']}</p>
          </div>
        </div>
      </article>
""")
        html_parts.append("    </section>")

    # Appendices
    html_parts.append("""
    <!-- Room Calibration -->
    <section class="category-block" id="calibration">
      <div class="category-header">
        <div class="category-number">Appendix A • Engineering Blueprint</div>
        <h2 class="category-title">Audiophile Calibration & Listening Room Setup Guide</h2>
        <div class="category-aesthetic">Optimization principles for planar magnetic headphones, nearfield reference monitors, and acoustic soundstaging.</div>
      </div>

      <div class="manifesto-box" style="margin-bottom: 30px;">
        <h3 style="color: var(--gold); margin-bottom: 12px; font-family: var(--font-serif); font-size: 1.4rem;">1. Equilateral Triangle Geometry & Ear-Level Alignment</h3>
        <p>
          For stereo loudspeaker listening, establish an exact equilateral triangle between your ears and the acoustic centers of the left and 
          right tweeters. Elevate speaker stands so high-frequency drivers sit exactly at seated ear level (typically 38-42 inches from the floor). 
          Toe in monitors gradually by 10 to 15 degrees until the center vocal image (the "phantom center") locks firmly into focused physical space 
          without narrowing soundstage width.
        </p>

        <h3 style="color: var(--gold); margin-top: 24px; margin-bottom: 12px; font-family: var(--font-serif); font-size: 1.4rem;">2. Subwoofer Crossover & Room Phase Alignment</h3>
        <p>
          When integrating active subwoofers with bookshelf or floorstanding monitors, set the low-pass crossover point between 60Hz and 80Hz. 
          Use test tracks with deep, articulated basslines (e.g., Massive Attack's "Angel" or Sade's "No Ordinary Love"). Continuously adjust 
          the sub's phase dial until the bass fundamental sounds tight, punchy, and completely in-phase with the main woofer attacks.
        </p>

        <h3 style="color: var(--gold); margin-top: 24px; margin-bottom: 12px; font-family: var(--font-serif); font-size: 1.4rem;">3. Planar Magnetic Headphone Current Delivery</h3>
        <p>
          Planar magnetic headphones (e.g., Audeze LCD series, HiFiMAN, Dan Clark Audio) feature ultra-thin diaphragms suspended between magnetic arrays. 
          Unlike high-impedance dynamic drivers, planars require high continuous electrical current rather than mere voltage swing. Pair planars with 
          a dedicated discrete Class-A or balanced solid-state headphone amplifier delivering at least 2 to 4 Watts per channel into 32 Ohms to avoid 
          transient compression on explosive drum hits (Radiohead's "Reckoner", The Breeders' "Cannonball").
        </p>

        <h3 style="color: var(--gold); margin-top: 24px; margin-bottom: 12px; font-family: var(--font-serif); font-size: 1.4rem;">4. Early Reflection Absorption</h3>
        <p>
          Place 2-inch to 4-inch dense acoustic panels (Owens Corning 703 or Rockwool Safe'n'Sound) at first reflection points on sidewalls and the 
          ceiling cloud. Use a mirror slid along the wall while seated in the listening chair: wherever you see the speaker tweeter reflected, 
          mount an acoustic absorber. This eliminates high-frequency comb filtering, sharpening the delicate stereo imaging of chamber folk 
          (Gillian Welch) and vocal choirs (Audrey Assad, The Brilliance).
        </p>
      </div>
    </section>

    <!-- Cross Reference Matrix -->
    <section class="category-block" id="matrix">
      <div class="category-header">
        <div class="category-number">Appendix B • Curatorial Bridges</div>
        <h2 class="category-title">Cross-Reference Matrix: Loved Library Records to Uncharted 100</h2>
        <div class="category-aesthetic">Direct mapping between the listener's most cherished library albums and their uncharted sister-masterpieces.</div>
      </div>

      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>Loved Library Album</th>
              <th>Recommended Uncharted Masterpiece</th>
              <th>Primary Shared Audiophile & Tonal Dimension</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><strong>The Sundays</strong> – <em>Reading, Writing and Arithmetic</em></td>
              <td><strong>Cocteau Twins</strong> – <em>Heaven or Las Vegas</em> (#016)</td>
              <td>Chorus-drenched shimmering guitar chime & ethereal melodic vocals</td>
            </tr>
            <tr>
              <td><strong>The Sundays</strong> – <em>Static & Silence</em></td>
              <td><strong>Real Estate</strong> – <em>Days</em> (#026)</td>
              <td>Fender clean tone warmth, Twin Reverb spring decay, pastoral jangle</td>
            </tr>
            <tr>
              <td><strong>Mac Miller</strong> – <em>Circles</em></td>
              <td><strong>Adrianne Lenker</strong> – <em>songs</em> (#023)</td>
              <td>Unfiltered whisper-track vocal intimacy, close-mic acoustic wood resonance</td>
            </tr>
            <tr>
              <td><strong>Mac Miller</strong> – <em>Circles</em></td>
              <td><strong>Saba</strong> – <em>CARE FOR ME</em> (#047)</td>
              <td>Intimate acoustic piano chords, live jazz pocket, vulnerable confessional grief</td>
            </tr>
            <tr>
              <td><strong>Nirvana</strong> – <em>MTV Unplugged in New York</em></td>
              <td><strong>Gillian Welch</strong> – <em>Time (The Revelator)</em> (#057)</td>
              <td>Raw live room acoustic tracking, zero pitch correction, physical dynamic presence</td>
            </tr>
            <tr>
              <td><strong>Nirvana</strong> – <em>MTV Unplugged in New York</em></td>
              <td><strong>Jeff Buckley</strong> – <em>Grace</em> (#032)</td>
              <td>Catastrophic vocal dynamic range, transcendent emotional release, raw telecaster chime</td>
            </tr>
            <tr>
              <td><strong>Norah Jones</strong> – <em>Come Away With Me</em></td>
              <td><strong>Cleo Sol</strong> – <em>Mother</em> (#004)</td>
              <td>Sacred living-room intimacy, warm upright bass, gentle nylon-string picking</td>
            </tr>
            <tr>
              <td><strong>Norah Jones</strong> – <em>Come Away With Me</em></td>
              <td><strong>Julia Jacklin</strong> – <em>Crushing</em> (#068)</td>
              <td>Unhurried vocal phrasing, authentic wooden room decay, heartbreak clarity</td>
            </tr>
            <tr>
              <td><strong>Lauryn Hill</strong> – <em>The Miseducation of Lauryn Hill</em></td>
              <td><strong>Erykah Badu</strong> – <em>Mama's Gun</em> (#002)</td>
              <td>Electric Lady 2-inch tape tracking, Soulquarian live groove, brass warmth</td>
            </tr>
            <tr>
              <td><strong>Lauryn Hill</strong> – <em>The Miseducation of Lauryn Hill</em></td>
              <td><strong>The Roots</strong> – <em>Things Fall Apart</em> (#043)</td>
              <td>Unquantized live hip-hop breakbeats, conscious street poetry, Bob Power mixing</td>
            </tr>
            <tr>
              <td><strong>Amy Winehouse</strong> – <em>Back to Black</em></td>
              <td><strong>Snoh Aalegra</strong> – <em>Ugh, those feels again</em> (#012)</td>
              <td>Velvet smoky alto vocals, sweeping orchestral strings, Motown/Stax nostalgia</td>
            </tr>
            <tr>
              <td><strong>Amy Winehouse</strong> – <em>Back to Black</em></td>
              <td><strong>Portishead</strong> – <em>Dummy</em> (#086)</td>
              <td>Dusty vinyl crackle, mournful Rhodes keys, torch-song heartbreak</td>
            </tr>
            <tr>
              <td><strong>Cannons</strong> – <em>Fever Dream</em></td>
              <td><strong>Sade</strong> – <em>Love Deluxe</em> (#003)</td>
              <td>Sultry, spacious basslines, nocturnal minimalism, silky vocal delivery</td>
            </tr>
            <tr>
              <td><strong>Cannons</strong> – <em>Fever Dream</em></td>
              <td><strong>The xx</strong> – <em>xx</em> (#088)</td>
              <td>Pitch-black soundstage silence, clean guitar delay, subterranean 808 sub-bass</td>
            </tr>
            <tr>
              <td><strong>Kacey Musgraves</strong> – <em>Golden Hour</em></td>
              <td><strong>Big Thief</strong> – <em>Dragon New Warm Mountain...</em> (#019)</td>
              <td>Modern organic folk warmth, inventive acoustic textures, cosmic love poetry</td>
            </tr>
            <tr>
              <td><strong>Kacey Musgraves</strong> – <em>Golden Hour</em></td>
              <td><strong>Sierra Ferrell</strong> – <em>Trail of Flowers</em> (#065)</td>
              <td>Gary Paczosa acoustic string staging, bell-like mountain vocal brilliance</td>
            </tr>
            <tr>
              <td><strong>Audrey Assad</strong> – <em>Inheritance</em></td>
              <td><strong>The Brilliance</strong> – <em>Brother</em> (#094)</td>
              <td>Sacred liturgical chamber strings, Steinway grand piano, reverent quietude</td>
            </tr>
            <tr>
              <td><strong>Audrey Assad</strong> – <em>Inheritance</em></td>
              <td><strong>All Sons & Daughters</strong> – <em>Poets & Saints</em> (#100)</td>
              <td>Historic European church acoustics, pipe organ overtones, intimate dual vocal harmony</td>
            </tr>
            <tr>
              <td><strong>Hillsong UNITED</strong> – <em>Empires</em></td>
              <td><strong>Citizens</strong> – <em>A Thousand Shores</em> (#097)</td>
              <td>Sweeping dream-pop synth pads, soaring alternative rock guitars, expansive soundstage</td>
            </tr>
            <tr>
              <td><strong>Hillsong UNITED</strong> – <em>Empires</em></td>
              <td><strong>Josh Garrels</strong> – <em>Love & War & The Sea In Between</em> (#099)</td>
              <td>Epic cinematic orchestral folk, multi-octave falsetto hymns, spiritual pilgrimage</td>
            </tr>
            <tr>
              <td><strong>Kendrick Lamar</strong> – <em>DAMN.*</em></td>
              <td><strong>GZA</strong> – <em>Liquid Swords</em> (#045)</td>
              <td>Dark, cinematic narrative sequencing, 12-bit sample grit, philosophical discipline</td>
            </tr>
            <tr>
              <td><strong>Kendrick Lamar</strong> – <em>DAMN.*</em></td>
              <td><strong>D'Angelo and The Vanguard</strong> – <em>Black Messiah</em> (#001)</td>
              <td>Uncompromising analog tape tracking, visceral sociopolitical fervor, virtuoso pocket</td>
            </tr>
            <tr>
              <td><strong>SZA</strong> – <em>Ctrl</em></td>
              <td><strong>Jazmine Sullivan</strong> – <em>Heaux Tales</em> (#021)</td>
              <td>Conversational vocal vulnerability, spoken-word interludes, virtuosic vocal runs</td>
            </tr>
            <tr>
              <td><strong>SZA</strong> – <em>Ctrl</em></td>
              <td><strong>Noname</strong> – <em>Room 25</em> (#049)</td>
              <td>Intimate live jazz trio, rapid conversational cadence, unapologetic feminine honesty</td>
            </tr>
            <tr>
              <td><strong>Billie Eilish</strong> – <em>HIT ME HARD AND SOFT</em></td>
              <td><strong>Elliott Smith</strong> – <em>Either/Or</em> (#033)</td>
              <td>Double-tracked whispered vocal proximity, unadorned acoustic fingerpicking</td>
            </tr>
            <tr>
              <td><strong>Billie Eilish</strong> – <em>HIT ME HARD AND SOFT</em></td>
              <td><strong>Björk</strong> – <em>Homogenic</em> (#072)</td>
              <td>Sudden tectonic electronic sub-bass eruptions colliding with acoustic strings</td>
            </tr>
            <tr>
              <td><strong>Lorde</strong> – <em>Melodrama</em></td>
              <td><strong>Kate Bush</strong> – <em>Hounds of Love</em> (#071)</td>
              <td>Theatrical avant-pop ambition, conceptual two-act architecture, soaring vocal art</td>
            </tr>
            <tr>
              <td><strong>Lorde</strong> – <em>Melodrama</em></td>
              <td><strong>Robyn</strong> – <em>Body Talk</em> (#078)</td>
              <td>Crying-in-the-club synthesizer pop perfection, cathartic electronic beats</td>
            </tr>
            <tr>
              <td><strong>Chappell Roan</strong> – <em>The Rise and Fall of a Midwest Princess</em></td>
              <td><strong>Caroline Polachek</strong> – <em>Desire, I Want to Turn Into You</em> (#075)</td>
              <td>Operatic vocal gymnastics, exuberant pop surrealism, Mediterranean acoustic flair</td>
            </tr>
            <tr>
              <td><strong>Chappell Roan</strong> – <em>The Rise and Fall of a Midwest Princess</em></td>
              <td><strong>Camera Obscura</strong> – <em>Let's Get Out of This Country</em> (#028)</td>
              <td>Baroque orchestral melodrama, witty romantic lyricism, chiming 60s pop hooks</td>
            </tr>
            <tr>
              <td><strong>Paramore</strong> – <em>After Laughter</em></td>
              <td><strong>Alvvays</strong> – <em>Blue Rev</em> (#018)</td>
              <td>Kinetic 12-string guitar jangle, sardonic lyrical wit, uncompressed dynamic punch</td>
            </tr>
            <tr>
              <td><strong>No Doubt</strong> – <em>Tragic Kingdom</em></td>
              <td><strong>The Breeders</strong> – <em>Last Splash</em> (#041)</td>
              <td>Playful irreverence, thunderous quiet-loud bass riffs, infectious pop-rock hooks</td>
            </tr>
            <tr>
              <td><strong>Adele</strong> – <em>21</em></td>
              <td><strong>Brandi Carlile</strong> – <em>By the Way, I Forgive You</em> (#061)</td>
              <td>Room-shaking chest voice power, raw acoustic heartbreak, string quartet warmth</td>
            </tr>
            <tr>
              <td><strong>Ella Langley</strong> – <em>Dandelion</em></td>
              <td><strong>Lucinda Williams</strong> – <em>Car Wheels on a Gravel Road</em> (#059)</td>
              <td>Southern backroad poetry, biting telecaster slide guitars, whiskey-tinged grit</td>
            </tr>
            <tr>
              <td><strong>Forrest Frank</strong> – <em>CHILD OF GOD</em></td>
              <td><strong>Liz Vice</strong> – <em>There's a Light</em> (#096)</td>
              <td>Joyous, organic gospel-soul brass, infectious rhythm, redemptive spiritual light</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

  </main>

  <footer>
    <div class="container">
      <p>THE UNCHARTED 100 • A CRITICAL AUDIOPHILE COMPANION</p>
      <p style="margin-top: 8px; font-size: 0.8rem; color: #555;">
        Compiled in September 2026 | Dedicated to Uninterrupted Front-to-Back Masterpieces
      </p>
    </div>
  </footer>

</body>
</html>
""")
    return "".join(html_parts)


def build():
    print("================================================================")
    print("THE UNCHARTED 100: CRITICAL AUDIOPHILE COMPANION COMPILER")
    print("================================================================")

    # 1. Verify Cover Art
    print("-> Verifying and cataloging 100 high-resolution album covers...")
    ensure_covers_downloaded()

    # 2. Write Markdown Companion
    md_content = generate_markdown()
    md_file = "uncharted_100_companion.md"
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"-> Successfully generated: {md_file} ({os.path.getsize(md_file):,} bytes)")

    # 3. Write HTML Companion Book
    html_content = generate_html()
    html_file = "uncharted_100_companion.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"-> Successfully generated: {html_file} ({os.path.getsize(html_file):,} bytes)")

    # 3b. Write Self-Contained Standalone HTML (All Images Base64 Embedded for iPad/Offline)
    standalone_html = html_content
    for alb in ALL_ALBUMS:
        lpath = alb.get("local_cover")
        if lpath and os.path.exists(lpath):
            with open(lpath, "rb") as img_f:
                b64_data = base64.b64encode(img_f.read()).decode("ascii")
                data_uri = f"data:image/jpeg;base64,{b64_data}"
                standalone_html = standalone_html.replace(f'src="{lpath}"', f'src="{data_uri}"')
    standalone_html = re.sub(r' onerror="[^"]*"', '', standalone_html)
    standalone_file = "uncharted_100_companion_standalone.html"
    with open(standalone_file, "w", encoding="utf-8") as f:
        f.write(standalone_html)
    print(f"-> Successfully generated: {standalone_file} ({os.path.getsize(standalone_file):,} bytes)")

    # 4. Generate PDF Book via Headless Chrome
    pdf_file = "uncharted_100_companion.pdf"
    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if os.path.exists(chrome_path):
        print(f"-> Found Google Chrome at: {chrome_path}")
        print("-> Rendering print-grade PDF book via Headless Chrome...")
        if os.path.exists(pdf_file):
            try:
                os.remove(pdf_file)
            except Exception:
                pass
        html_path = os.path.abspath(html_file)
        pdf_path = os.path.abspath(pdf_file)
        cmd = [
            chrome_path,
            "--headless",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={pdf_path}",
            f"file://{html_path}"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
            if os.path.exists(pdf_file) and os.path.getsize(pdf_file) > 10000:
                print(f"-> Successfully generated: {pdf_file} ({os.path.getsize(pdf_file):,} bytes)")
            else:
                print(f"-> Chrome PDF warning: {res.stderr}")
        except Exception as e:
            print(f"-> Chrome PDF render error: {e}")
    else:
        print("-> Google Chrome not found at standard path. Skipping automated PDF render.")

    print("\nCompilation Complete! All artifacts generated in current directory.")


if __name__ == "__main__":
    build()
