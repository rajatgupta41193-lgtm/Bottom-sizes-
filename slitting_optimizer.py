import math
import os

SIZE_FILE = "saved_slitting_sizes.txt"
OUTPUT_FILE = "slitting_schedule.txt"

def load_or_create_sizes():
    """Loads baseline sizes from disk or prompts the user to set them up permanently."""
    if os.path.exists(SIZE_FILE):
        try:
            with open(SIZE_FILE, "r", encoding="utf-8") as f:
                sizes = [float(line.strip()) for line in f if line.strip()]
            if sizes:
                print(f"✅ Loaded {len(sizes)} permanent slitting sizes from '{SIZE_FILE}': {sorted(sizes)}")
                use_existing = input("Do you want to use these saved sizes? (Y/N): ").strip().lower()
                if use_existing != 'n':
                    return sorted(sizes, reverse=True)
        except Exception as e:
            print(f"⚠️ Error reading saved sizes: {e}. Let's set them up again.")

    # If no file exists or user wants to overwrite
    print("\n--- Permanent Size Configuration Setup ---")
    sizes = []
    while True:
        size_input = input("Enter a Slitting Size (mm) [or type 'done' to save]: ").strip().lower()
        if size_input == 'done':
            if not sizes:
                print("❌ You must enter at least one size.")
                continue
            break
        try:
            sz = float(size_input)
            if sz <= 0:
                print("❌ Size must be greater than zero.")
                continue
            if sz not in sizes:
                sizes.append(sz)
        except ValueError:
            print("❌ Invalid input! Numbers only.")

    # Save to disk for all future runs
    try:
        with open(SIZE_FILE, "w", encoding="utf-8") as f:
            for sz in sorted(sizes):
                f.write(f"{sz}\n")
        print(f"💾 Profile saved successfully to '{SIZE_FILE}'. You won't be asked for sizes next time!")
    except IOError as e:
        print(f"⚠️ Warning: Could not save sizes to disk: {e}")

    return sorted(sizes, reverse=True)

def get_inputs():
    print("\n--- Proportional Slitting Optimizer ---")
    try:
        master_size = float(input("Enter Master Reel Width (mm): "))
        total_weight = float(input("Enter Total Master Reel Weight (kg): "))
        
        # Load the permanent sizing checklist
        available_sizes = load_or_create_sizes()
        
        demands = {}
        print("\nEnter the weight (KG) required for each size. Enter '0' if a size is not needed today.")
        
        for size in available_sizes:
            while True:
                weight_input = input(f"Required Weight (kg) for {int(size) if size.is_integer() else size}mm: ").strip()
                try:
                    req_weight = float(weight_input)
                    if req_weight < 0:
                        print("❌ Weight cannot be negative.")
                        continue
                    if req_weight > 0:
                        demands[size] = req_weight
                    break
                except ValueError:
                    print("❌ Invalid input! Please enter a number.")
                    
        if not demands:
            print("❌ No weights were entered. Cannot process a blank run.")
            return None, None, None
            
        return master_size, total_weight, demands
    except ValueError:
        print("❌ Invalid input format. Restarting.")
        return None, None, None

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

def generate_schedule():
    inputs = get_inputs()
    if not inputs or not inputs[0]:
        return
    master_size, total_weight, weight_demands = inputs
        
    weight_per_mm = total_weight / master_size
    sizes = sorted(list(weight_demands.keys()), reverse=True)
    
    patterns_with_trim = find_valid_patterns(master_size, sizes)
    if not patterns_with_trim:
        print(f"\n❌ No combinations can achieve a trim between 3mm and 5mm with the active sizes.")
        return

    schedule = []
    remaining_weight = weight_demands.copy()
    total_produced_weight = {sz: 0.0 for sz in weight_demands}
    
    while any(val > 0.01 for val in remaining_weight.values()):
        cap_reached_sizes = set()
        for sz, req in weight_demands.items():
            if total_produced_weight[sz] >= (req * 1.15):
                cap_reached_sizes.add(sz)
        
        best_pattern = None
        best_trim = None
        best_score = float('-inf')
        
        for pattern, trim in patterns_with_trim:
            score = calculate_proportional_score(pattern, remaining_weight, cap_reached_sizes)
            score -= (trim * 0.05)  
            
            if score > best_score:
                best_score = score
                best_pattern = pattern
                best_trim = trim
                
        if not best_pattern or best_score < -500:
            for pattern, trim in patterns_with_trim:
                if any(remaining_weight[sz] > 0 for sz in pattern) and not any(sz in cap_reached_sizes for sz in pattern):
                    best_pattern = pattern
                    best_trim = trim
                    break
            if not best_pattern:
                print("\n⚠️ Safe processing stopped to prevent exceeding the 15% overproduction limit.")
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

        schedule.append({
            "pattern": best_pattern,
            "repeats": max_repeats,
            "trim": best_trim
        })
        
        for sz in best_pattern:
            delivered_weight = sz * weight_per_mm * max_repeats
            remaining_weight[sz] -= delivered_weight
            total_produced_weight[sz] += delivered_weight

    output_lines = ["="*20 + " COPY READY OUTPUT " + "="*20]
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
        trim_weight_per_reel = trim_size * weight_per_mm
        total_trim_weight_for_run = trim_weight_per_reel * run['repeats']
        total_reels_used += run['repeats']
        
        output_lines.append(f"Total width: {int(total_width) if total_width.is_integer() else total_width} mm")
        output_lines.append(f"Trim size: {trim_size} mm")
        output_lines.append(f"Trim weight: {total_trim_weight_for_run:.3f} kg\n")
        
    output_lines.append(f"Total Master Reels Consumed: {total_reels_used}")
    output_lines.append("="*59)

    final_output_text = "\n".join(output_lines)
    print("\n" + final_output_text)
    
    try:
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_output_text)
        print(f"\n💾 Success! Output data saved to: {os.path.abspath(OUTPUT_FILE)}")
    except IOError as e:
        print(f"\n❌ Error writing file to disk: {e}")

if __name__ == "__main__":
    generate_schedule()
