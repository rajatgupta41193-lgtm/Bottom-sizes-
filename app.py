import streamlit as st
import math

# =====================================================================
# PAGE CONFIG
# =====================================================================
st.set_page_config(
    page_title="Reel Slitting Optimizer",
    page_icon="✂️",
    layout="wide"
)

# =====================================================================
# CUSTOM CSS — Industrial dark theme
# =====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=Barlow+Condensed:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Barlow Condensed', sans-serif;
}

.stApp {
    background-color: #0f1117;
    color: #e8e4dc;
}

/* Title styling */
h1 { font-family: 'Barlow Condensed', sans-serif !important; font-size: 2.6rem !important; font-weight: 700 !important; letter-spacing: 2px !important; color: #f0a500 !important; text-transform: uppercase; }
h2, h3, h4 { font-family: 'Barlow Condensed', sans-serif !important; color: #c8c0b0 !important; letter-spacing: 1px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #181c24 !important;
    border-right: 2px solid #2a2e3a;
}
[data-testid="stSidebar"] * { color: #c8c0b0 !important; }
[data-testid="stSidebar"] h2 { color: #f0a500 !important; }

/* Input fields */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background-color: #1e2230 !important;
    border: 1px solid #3a3f50 !important;
    border-radius: 4px !important;
    color: #e8e4dc !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.9rem !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #f0a500 !important;
    box-shadow: 0 0 0 2px rgba(240,165,0,0.15) !important;
}

/* Labels */
label, .stNumberInput label, .stTextInput label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #8a8880 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Primary button */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #f0a500, #d4820a) !important;
    color: #0f1117 !important;
    border: none !important;
    border-radius: 4px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1.1rem !important;
    letter-spacing: 2px !important;
    text-transform: uppercase;
    padding: 0.5rem 2rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #ffc107, #f0a500) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 15px rgba(240,165,0,0.3) !important;
}

/* Secondary button */
.stButton > button {
    background-color: #1e2230 !important;
    color: #c8c0b0 !important;
    border: 1px solid #3a3f50 !important;
    border-radius: 4px !important;
    font-family: 'Barlow Condensed', sans-serif !important;
    letter-spacing: 1px;
}

/* Text area */
textarea {
    background-color: #0a0d14 !important;
    border: 1px solid #2a2e3a !important;
    color: #a8f0a0 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    border-radius: 4px !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background-color: #181c24;
    border: 1px solid #2a2e3a;
    border-radius: 6px;
    padding: 1rem;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #f0a500 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 1.6rem !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #8a8880 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    text-transform: uppercase;
}

/* Success / warning / error */
[data-testid="stAlert"] {
    border-radius: 4px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}

/* Divider */
hr { border-color: #2a2e3a !important; }

/* Form border */
[data-testid="stForm"] {
    border: 1px solid #2a2e3a;
    border-radius: 8px;
    padding: 1.5rem;
    background-color: #13161e;
}

/* Expander */
[data-testid="stExpander"] {
    background-color: #13161e !important;
    border: 1px solid #2a2e3a !important;
    border-radius: 6px !important;
}

/* Pattern card custom */
.pattern-card {
    background: #181c24;
    border: 1px solid #2a2e3a;
    border-left: 4px solid #f0a500;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: #c8c0b0;
}
.pattern-card .run-title {
    color: #f0a500;
    font-weight: 600;
    font-size: 1rem;
    letter-spacing: 1px;
    margin-bottom: 0.4rem;
}
.pattern-card .size-line {
    color: #e8e4dc;
}
.pattern-card .trim-line {
    color: #e05050;
    margin-top: 0.3rem;
}
.pattern-card .width-line {
    color: #60b8a0;
    margin-top: 0.2rem;
}

.section-header {
    font-family: 'Barlow Condensed', sans-serif;
    font-size: 1.3rem;
    font-weight: 700;
    color: #f0a500;
    text-transform: uppercase;
    letter-spacing: 3px;
    border-bottom: 2px solid #2a2e3a;
    padding-bottom: 0.4rem;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================

def find_valid_patterns(master_size, sizes, min_trim=3.0, max_trim=5.0):
    valid_patterns = []
    def backtrack(current_combo, current_width, start_index):
        trim = master_size - current_width
        if min_trim <= trim <= max_trim:
            valid_patterns.append((list(current_combo), round(trim, 2)))
        if current_width >= master_size - min_trim:
            return
        for i in range(start_index, len(sizes)):
            size = sizes[i]
            if current_width + size <= master_size - min_trim:
                current_combo.append(size)
                backtrack(current_combo, current_width + size, i)
                current_combo.pop()
    backtrack([], 0.0, 0)
    return valid_patterns


def calculate_proportional_score(pattern, remaining_weight_demands, cap_reached_sizes):
    pattern_counts = {}
    for size in pattern:
        if size in cap_reached_sizes:
            return float('-inf')
        pattern_counts[size] = pattern_counts.get(size, 0) + 1

    total_remaining_weight = sum(remaining_weight_demands.values())
    if total_remaining_weight == 0:
        return 0

    total_pattern_items = len(pattern)
    score = 0
    for size, pattern_qty in pattern_counts.items():
        rem_weight = remaining_weight_demands.get(size, 0.0)
        if rem_weight <= 0:
            score -= 50
            continue
        weight_ratio = rem_weight / total_remaining_weight
        pattern_ratio = pattern_qty / total_pattern_items
        ratio_error = abs(weight_ratio - pattern_ratio)
        score += (1.0 - ratio_error) * 20
    return score


def run_optimization(master_size, total_weight, weight_demands):
    """
    Core optimization engine. Returns (schedule, total_produced_weight, safe_stop).
    schedule = list of {pattern, repeats, trim}
    """
    weight_per_mm = total_weight / master_size
    sizes = sorted(list(weight_demands.keys()), reverse=True)
    patterns_with_trim = find_valid_patterns(master_size, sizes)

    if not patterns_with_trim:
        return None, None, False

    schedule = []
    remaining_weight = weight_demands.copy()
    total_produced_weight = {sz: 0.0 for sz in weight_demands}
    safe_stop_triggered = False

    while any(val > 0.01 for val in remaining_weight.values()):
        cap_reached_sizes = set()
        for sz, req in weight_demands.items():
            if total_produced_weight[sz] >= (req * 1.15):
                cap_reached_sizes.add(sz)

        best_pattern, best_trim, best_score = None, None, float('-inf')
        for pattern, trim in patterns_with_trim:
            score = calculate_proportional_score(pattern, remaining_weight, cap_reached_sizes)
            score -= (trim * 0.05)
            if score > best_score:
                best_score, best_pattern, best_trim = score, pattern, trim

        if not best_pattern or best_score < -500:
            for pattern, trim in patterns_with_trim:
                if any(remaining_weight[sz] > 0 for sz in pattern) and \
                   not any(sz in cap_reached_sizes for sz in pattern):
                    best_pattern, best_trim = pattern, trim
                    break
            if not best_pattern:
                safe_stop_triggered = True
                break

        weight_per_run_by_size = {
            sz: sz * best_pattern.count(sz) * weight_per_mm
            for sz in set(best_pattern)
        }
        max_repeats = float('inf')
        for sz, w_per_run in weight_per_run_by_size.items():
            if remaining_weight[sz] > 0:
                possible_repeats = math.ceil(remaining_weight[sz] / w_per_run)
                if possible_repeats < max_repeats:
                    max_repeats = possible_repeats

        if max_repeats == float('inf') or max_repeats == 0:
            max_repeats = 1

        for sz, w_per_run in weight_per_run_by_size.items():
            allowed_extra_weight = (weight_demands[sz] * 1.15) - total_produced_weight[sz]
            allowed_repeats = math.floor(allowed_extra_weight / w_per_run)
            if allowed_repeats < max_repeats:
                max_repeats = max(1, allowed_repeats)

        schedule.append({"pattern": best_pattern, "repeats": max_repeats, "trim": best_trim})
        for sz in best_pattern:
            delivered_weight = sz * weight_per_mm * max_repeats
            remaining_weight[sz] -= delivered_weight
            total_produced_weight[sz] += delivered_weight

    return schedule, total_produced_weight, safe_stop_triggered


# =====================================================================
# SESSION STATE
# =====================================================================
if 'saved_sizes' not in st.session_state:
    st.session_state['saved_sizes'] = [47.0, 50.0, 53.0, 55.0, 65.0]

# =====================================================================
# SIDEBAR
# =====================================================================
st.sidebar.markdown("## ⚙️ Size Profile")
st.sidebar.markdown("Define your master child/bottom sizes:")

new_sizes_input = st.sidebar.text_input(
    "Profile Sizes (comma-separated mm):",
    value=", ".join(map(str, sorted([int(x) if x == int(x) else x
                                     for x in st.session_state['saved_sizes']]))),
    help="Edit sizes here — updates instantly."
)

try:
    parsed_sizes = sorted(
        [float(x.strip()) for x in new_sizes_input.split(",") if x.strip()],
        reverse=True
    )
    if parsed_sizes:
        st.session_state['saved_sizes'] = parsed_sizes
except ValueError:
    st.sidebar.error("Numbers separated by commas only.")

st.sidebar.markdown("---")
st.sidebar.markdown("**Trim Rule:** 3 mm – 5 mm")
st.sidebar.markdown("**Overproduction Cap:** 115%")
st.sidebar.markdown("**Algorithm:** Proportional greedy + ratio scoring")

# =====================================================================
# TITLE
# =====================================================================
st.markdown("# ✂️ REEL SLITTING OPTIMIZER")
st.markdown(
    "<p style='color:#8a8880;font-family:IBM Plex Mono,monospace;font-size:0.85rem;"
    "letter-spacing:1px;margin-top:-0.8rem;'>PROPORTIONAL CUTTING SCHEDULE · 3–5 mm TRIM RULE · 115% CAP</p>",
    unsafe_allow_html=True
)
st.write("---")

# =====================================================================
# INPUT FORM
# =====================================================================
with st.form("slitting_form"):
    st.markdown('<div class="section-header">Master Reel Parameters</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        master_size = st.number_input(
            "Master Reel Width (mm):", min_value=1.0, value=500.0, step=1.0
        )
    with col2:
        total_weight = st.number_input(
            "Total Master Reel Weight (kg):", min_value=0.1, value=150.0, step=0.5
        )

    st.markdown('<div class="section-header" style="margin-top:1.5rem;">Target Weights per Size (kg)</div>',
                unsafe_allow_html=True)
    st.markdown(
        "<p style='color:#8a8880;font-family:IBM Plex Mono,monospace;font-size:0.75rem;"
        "margin-top:-0.5rem;'>Leave at 0.0 to exclude a size from this run.</p>",
        unsafe_allow_html=True
    )

    weight_inputs = {}
    num_sizes = len(st.session_state['saved_sizes'])
    n_cols = min(num_sizes, 5)
    input_cols = st.columns(n_cols)

    for idx, size in enumerate(st.session_state['saved_sizes']):
        col_target = input_cols[idx % n_cols]
        display_size = int(size) if size == int(size) else size
        with col_target:
            weight_inputs[size] = st.number_input(
                f"{display_size} mm:",
                min_value=0.0, value=0.0, step=1.0,
                key=f"size_{size}"
            )

    st.write("")
    submit_btn = st.form_submit_button("⚡ OPTIMIZE CUTTING SCHEDULE", type="primary")

# =====================================================================
# COMPUTATION & OUTPUT
# =====================================================================
if submit_btn:
    weight_demands = {sz: val for sz, val in weight_inputs.items() if val > 0}
    skipped_sizes  = [int(sz) if sz == int(sz) else sz
                      for sz, val in weight_inputs.items() if val == 0]

    if not weight_demands:
        st.error("❌ Enter a weight > 0 kg for at least one size.")
    else:
        with st.spinner("Computing optimal cutting schedule…"):
            schedule, total_produced_weight, safe_stop = run_optimization(
                master_size, total_weight, weight_demands
            )

        if schedule is None:
            st.error(
                f"❌ No valid combinations achieve a 3–5 mm trim on a {master_size} mm "
                f"master with the selected sizes."
            )
        else:
            # ── Alerts ──────────────────────────────────────────────
            if safe_stop:
                st.warning(
                    "⚠️ Optimization halted early to prevent exceeding the 115% "
                    "overproduction cap on one or more sizes."
                )

            st.success("🎉 Schedule computed — review below and copy your results.")

            # ── Summary metrics ──────────────────────────────────────
            st.write("---")
            st.markdown('<div class="section-header">Summary</div>', unsafe_allow_html=True)

            total_reels = sum(r["repeats"] for r in schedule)
            total_trim_weight = sum(
                r["trim"] * (total_weight / master_size) * r["repeats"]
                for r in schedule
            )
            num_patterns = len(schedule)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Run Patterns", num_patterns)
            m2.metric("Total Reels Used", total_reels)
            m3.metric("Total Trim Waste", f"{total_trim_weight:.2f} kg")
            m4.metric("Active Sizes", len(weight_demands))

            # ── Production vs Target table ───────────────────────────
            st.write("---")
            st.markdown('<div class="section-header">Production vs Target</div>', unsafe_allow_html=True)

            rows = []
            for sz in sorted(weight_demands.keys()):
                target  = weight_demands[sz]
                produced = total_produced_weight.get(sz, 0.0)
                variance = produced - target
                pct      = (produced / target * 100) if target > 0 else 0
                display_sz = int(sz) if sz == int(sz) else sz
                rows.append({
                    "Size (mm)":      display_sz,
                    "Target (kg)":    round(target, 2),
                    "Produced (kg)":  round(produced, 3),
                    "Variance (kg)":  f"+{round(variance,3)}" if variance >= 0 else str(round(variance,3)),
                    "% of Target":    f"{pct:.1f}%",
                })

            import pandas as pd
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # ── Pattern cards ────────────────────────────────────────
            st.write("---")
            st.markdown('<div class="section-header">Run Patterns</div>', unsafe_allow_html=True)

            weight_per_mm = total_weight / master_size

            for idx, run in enumerate(schedule, 1):
                counts      = {}
                total_width = 0
                for sz in run["pattern"]:
                    counts[sz] = counts.get(sz, 0) + 1

                size_lines = []
                for sz in sorted(counts.keys()):
                    cnt        = counts[sz]
                    line_width = sz * cnt
                    total_width += line_width
                    dsz        = int(sz) if sz == int(sz) else sz
                    dlw        = int(line_width) if line_width == int(line_width) else line_width
                    size_lines.append(f"&nbsp;&nbsp;{dsz} mm × {cnt} = {dlw} mm")

                trim_wt = run["trim"] * weight_per_mm * run["repeats"]
                dtw     = int(total_width) if total_width == int(total_width) else total_width

                card_html = f"""
                <div class="pattern-card">
                  <div class="run-title">RUN #{idx} &nbsp;·&nbsp; REPEAT × {run['repeats']}</div>
                  {'<br>'.join(f'<span class="size-line">{l}</span>' for l in size_lines)}
                  <div class="width-line">──────────────────────────────<br>&nbsp;&nbsp;Total width : {dtw} mm</div>
                  <div class="trim-line">&nbsp;&nbsp;Trim : {run['trim']} mm &nbsp;|&nbsp; Trim weight : {trim_wt:.3f} kg</div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)

            # ── Copyable output ──────────────────────────────────────
            st.write("---")
            st.markdown('<div class="section-header">Copy-Ready Output</div>', unsafe_allow_html=True)

            output_lines = ["========== REEL SLITTING SCHEDULE =========="]
            if skipped_sizes:
                output_lines.append(
                    f"Skipped (0 kg): {', '.join(map(str, sorted(skipped_sizes)))}\n"
                )

            total_reels_used = 0
            for idx, run in enumerate(schedule, 1):
                output_lines.append(f"--- RUN #{idx}  (x{run['repeats']}) ---")
                counts = {}
                for sz in run["pattern"]:
                    counts[sz] = counts.get(sz, 0) + 1
                total_width = 0
                for sz in sorted(counts.keys()):
                    cnt = counts[sz]
                    lw  = sz * cnt
                    total_width += lw
                    dsz = int(sz) if sz == int(sz) else sz
                    dlw = int(lw) if lw == int(lw) else lw
                    output_lines.append(f"  {dsz} mm * {cnt} = {dlw} mm")
                dtw       = int(total_width) if total_width == int(total_width) else total_width
                trim_wt   = run["trim"] * weight_per_mm * run["repeats"]
                total_reels_used += run["repeats"]
                output_lines.append(f"  Total width  : {dtw} mm")
                output_lines.append(f"  Trim         : {run['trim']} mm")
                output_lines.append(f"  Trim weight  : {trim_wt:.3f} kg\n")

            output_lines.append(f"Total Master Reels : {total_reels_used}")
            output_lines.append(f"Total Trim Waste   : {total_trim_weight:.3f} kg")
            output_lines.append("============================================")

            st.text_area(
                "Cutting Schedule:",
                value="\n".join(output_lines),
                height=420,
                label_visibility="collapsed"
            )
