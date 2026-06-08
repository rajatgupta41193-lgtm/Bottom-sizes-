import streamlit as st
import math

# --- App Configuration & Styling ---
st.set_page_config(page_title="Reel Slitting Optimizer", page_icon="✂️", layout="centered")
st.title("✂️ Proportional Reel Slitting Optimizer")
st.markdown("Optimize master reel cutting patterns based on proportional KG demands with a strict 3mm–5mm trim rule.")

# --- Helper Functions ---
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

# --- Sidebar: Permanent Size Profile Setup ---
st.sidebar.header("⚙️ Sizing Setup")
st.sidebar.markdown("Define your stable bottom/child sizes below:")

# Initialize session state for persistent sizes if not already present
if 'saved_sizes' not in st.session_state:
    st.session_state['saved_sizes'] = [47.0, 50.0, 53.0, 55.0, 65.0]  # default fallback sizes

new_sizes_input = st.sidebar.text_input(
    "Edit Profile Sizes (comma-separated mm):", 
    value=", ".join(map(str, sorted([int(x) if x.is_integer() else x for x in st.session_state['saved_sizes']]))),
    help="Changes made here update your master sizing options instantly."
)

# Parse sizing entries dynamically from user input
try:
    parsed_sizes = sorted([float(x.strip()) for x in new_sizes_input.split(",") if x.strip()], reverse=True)
    if parsed_sizes:
        st.session_state['saved_sizes'] = parsed_sizes
except ValueError:
    st.sidebar.error("Please enter numbers separated by commas only.")

# --- Main Form UI: Inputs ---
with st.form("slitting_form"):
    col1, col2 = st.columns(2)
    with col1:
        master_size = st.number_input("Master Reel Width (mm):", min_value=1.0, value=500.0, step=1.0)
    with col2:
        total_weight = st.number_input("Total Master Reel Weight (kg):", min_value=0.1, value=150.0, step=0.5)
        
    st.markdown("#### ⚖️ Enter Target Weights Required (kg)")
    st.markdown("_Leave at 0.0 if a size is not needed for this batch execution._")
    
    weight_inputs = {}
    # Dynamically generate weight fields for each size in your persistent profile
    input_cols = st.columns(min(len(st.session_state['saved_sizes']), 4))
    for idx, size in enumerate(st.session_state['saved_sizes']):
        col_target = input_cols[idx % 4]
        display_size = int(size) if size.is_integer() else size
        with col_target:
            weight_inputs[size] = st.number_input(f"{display_size} mm:", min_value=0.0, value=0.0, step=1.0, key=f"size_{size}")
            
    submit_btn = st.form_submit_button("⚡ Optimize Cutting Schedule", type="primary")

# --- Core Computation & Output Presentation ---
if submit_btn:
    weight_demands = {sz: val for sz, val in weight_inputs.items() if val > 0}
    skipped_sizes = [int(sz) if sz.is_integer() else sz for sz, val in weight_inputs.items() if val == 0]
    
    if not weight_demands:
        st.error("❌ Please enter a weight greater than 0 kg for at least one slitting size.")
    else:
        weight_per_mm = total_weight / master_size
        sizes = sorted(list(weight_demands.keys()), reverse=True)
        patterns_with_trim = find_valid_patterns(master_size, sizes)
        
        if not patterns_with_trim:
            st.error(f"❌ No combinations can achieve a trim between 3mm and 5mm with active sizes on a {master_size}mm width.")
        else:
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
                        if any(remaining_weight[sz] > 0 for sz in pattern) and not any(sz in cap_reached_sizes for sz in pattern):
                            best_pattern, best_trim = pattern, trim
                            break
                    if not best_pattern:
                        safe_stop_triggered = True
                        break
                        
                weight_per_run_by_size = {sz: sz * best_pattern.count(sz) * weight_per_mm for sz in set(best_pattern)}
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

            # Format the output block for text box presentation
            output_lines = ["==================== COPY READY OUTPUT ===================="]
            if skipped_sizes:
                output_lines.append(f"Skipped Sizes (0 kg): {', '.join(map(str, sorted(skipped_sizes)))}\n")
                
            total_reels_used = 0
            for idx, run in enumerate(schedule, 1):
                output_lines.append(f"--- RUN PATTERN #{idx} (Repeat x {run['repeats']}) ---")
                counts = {}
                for sz in run['pattern']:
                    counts[sz] = counts.get(sz, 0) + 1
                    
                total_width = 0
                for sz in sorted(counts.keys()):
                    count = counts[sz]
                    line_width = sz * count
                    total_width += line_width
                    output_lines.append(f"{int(sz) if sz.is_integer() else sz} mm * {count} = {int(line_width) if line_width.is_integer() else line_width} mm")
                    
                trim_size = run['trim']
                trim_weight_for_run = (trim_size * weight_per_mm) * run['repeats']
                total_reels_used += run['repeats']
                
                output_lines.append(f"Total width: {int(total_width) if total_width.is_integer() else total_width} mm")
                output_lines.append(f"Trim size: {trim_size} mm")
                output_lines.append(f"Trim weight: {trim_weight_for_run:.3f} kg\n")
                
            output_lines.append(f"Total Master Reels Consumed: {total_reels_used}")
            output_lines.append("===========================================================")
            final_output_text = "\n".join(output_lines)
            
            if safe_stop_triggered:
                st.warning("⚠️ Optimization stopped early for some items to safeguard against exceeding the 15% overproduction limit.")
                
            st.success("🎉 Calculation Complete! Copy your results below:")
            
            # Text area display with built-in copy button natively provided by Streamlit
            st.text_area("Cutting Schedule Output:", value=final_output_text, height=400)
