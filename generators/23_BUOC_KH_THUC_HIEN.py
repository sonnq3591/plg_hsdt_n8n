#!/usr/bin/env python3
"""
23_BUOC_KH_THUC_HIEN.py - Generate 23-step timeline graph with exact format
Uses extracted thoi_gian_hoan_thanh data and applies ratio scaling
"""

import matplotlib.pyplot as plt
import pandas as pd
import textwrap
import os
import json
from pathlib import Path
from io import StringIO

def read_batch_id():
    """Read current batch ID"""
    try:
        base_dir = Path(__file__).parent.parent
        batch_file = base_dir / "current_batch.txt"
        with open(batch_file, "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("❌ current_batch.txt not found!")
        return None

def load_extracted_time():
    """Load thoi_gian_hoan_thanh from extracted data"""
    batch_id = read_batch_id()
    if not batch_id:
        return "120 ngày"  # Default fallback
    
    base_dir = Path(__file__).parent.parent
    master_file = base_dir / batch_id / "extracted_data" / "master_data.json"
    
    try:
        with open(master_file, 'r', encoding='utf-8') as f:
            master_data = json.load(f)
        
        placeholders = master_data.get("placeholders", {})
        time_data = placeholders.get("thoi_gian_hoan_thanh", {})
        content = time_data.get("content", "120 ngày")
        
        print(f"📊 Extracted time: {content}")
        return content
        
    except Exception as e:
        print(f"⚠️ Could not load extracted time: {e}")
        return "120 ngày"  # Default fallback

def extract_days_from_time(time_str):
    """Extract number of days from time string"""
    import re
    numbers = re.findall(r'\d+', time_str)
    if numbers:
        return int(numbers[0])
    return 120  # Default fallback

def generate_23_buoc_graph():
    """Generate the 23-step timeline graph"""
    
    # Get extracted time and calculate scaling
    extracted_time = load_extracted_time()
    target_days = extract_days_from_time(extracted_time)
    
    print(f"🎯 Target total days: {target_days}")
    
    # Hardcoded CSV data from the image (base ratios sum to 100)
    csv_data = """Task,So_ngay
Giao nhận tài liệu và lập biên bản giao nhận tài liệu,0.5
Vận chuyển tài liệu từ kho bảo quản đến địa điểm chỉnh lý (~100m),1
Vệ sinh sơ bộ tài liệu,1
Khảo sát và biên soạn các văn bản hướng dẫn chỉnh lý,1
Phân loại tài liệu theo Hướng dẫn phân loại,20
Lập hồ sơ hoặc chỉnh sửa hoàn thiện hồ sơ theo Hướng dẫn lập hồ sơ,30
Viết các trường thông tin vào phiếu tin,2
Kiểm tra chỉnh sửa hồ sơ và phiếu tin,1
Hệ thống hóa phiếu tin theo phương án phân loại,1
Hệ thống hóa hồ sơ theo phiếu tin,1
Biên mục hồ sơ,15
Kiểm tra và chỉnh sửa việc biên mục hồ sơ,1
Ghi số hồ sơ chính thức vào phiếu tin và lên bìa hồ sơ,6
Vệ sinh tài liệu tháo bỏ ghim kẹp làm phẳng và đưa tài liệu vào bìa hồ sơ,1
Đưa hồ sơ vào hộp (cặp),2
Viết/in và dán nhãn hộp (cặp),2
Vận chuyển tài liệu vào kho và xếp lên giá,1
Giao nhận tài liệu sau chỉnh lý và lập Biên bản giao nhận tài liệu,1
Nhập phiếu tin vào cơ sở dữ liệu,5
Kiểm tra chỉnh sửa việc nhập phiếu tin,1
Lập mục lục hồ sơ,4
Thống kê bó gói lập danh mục và viết thuyết minh tài liệu loại,1
Kết thúc chỉnh lý,1"""
    
    # Convert to DataFrame
    df = pd.read_csv(StringIO(csv_data))
    
    # Calculate scaling ratio
    base_total = df['So_ngay'].sum()  # Should be 100
    scaling_ratio = target_days / base_total
    
    print(f"📊 Base total: {base_total} days")
    print(f"📊 Scaling ratio: {scaling_ratio:.3f}")
    
    # Apply scaling and round up
    df['Days_Scaled'] = (df['So_ngay'] * scaling_ratio).apply(lambda x: max(1, round(x)))
    
    # Verify total
    scaled_total = df['Days_Scaled'].sum()
    print(f"📊 Scaled total: {scaled_total} days")
    
    # Wrap task names every 2 words
    def wrap_text(text, words_per_line=2):
        words = text.split()
        return '\n'.join([' '.join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)])

    wrapped_labels = [wrap_text(task, 2) for task in df["Task"]]

    # Calculate layout adjustments
    max_lines = max(label.count('\n') + 1 for label in wrapped_labels)
    bottom_margin = 0.4 + 0.03 * max_lines  # Increased bottom margin for x-axis labels
    fig_height = 12 + 0.5 * max_lines

    # Create figure
    fig, ax = plt.subplots(figsize=(26, fig_height))

    # Line plot using regular x positions
    x = df.index
    ax.plot(x, df['Days_Scaled'], marker='o', color='red', linestyle='-')
    ax.set_title("KẾ HOẠCH THỰC HIỆN CÔNG VIỆC (23 BƯỚC)", fontsize=20, pad=25)
    ax.set_ylabel("Số ngày", fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(wrapped_labels, rotation=0, ha='center', fontsize=11.5)
    ax.grid(True, axis='y', linestyle='--', alpha=0.6)

    # Set y-axis limits with extra space at top for labels
    max_y = df['Days_Scaled'].max()
    ax.set_ylim(0, max_y * 1.15)  # Add 15% extra space at top

    # Annotate data points
    for i, y in enumerate(df['Days_Scaled']):
        ax.annotate(str(y), (x[i], y), textcoords="offset points", xytext=(0, 10), va='bottom', ha='center', fontsize=12)

    plt.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=bottom_margin)
    
    # Save to pictures folder
    batch_id = read_batch_id()
    if batch_id:
        base_dir = Path(__file__).parent.parent
        pictures_dir = base_dir / batch_id / "pictures"
        pictures_dir.mkdir(exist_ok=True)
        
        output_file = pictures_dir / "23_BUOC_KH_THUC_HIEN.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"💾 Graph saved: {output_file}")
    else:
        # Fallback to current directory
        plt.savefig("23_BUOC_KH_THUC_HIEN.png", dpi=300, bbox_inches='tight')
        print("💾 Graph saved: 23_BUOC_KH_THUC_HIEN.png")
    
    plt.show()

def main():
    print("📊 23-Step Timeline Graph Generator")
    print("=" * 50)
    
    try:
        generate_23_buoc_graph()
        print("\n🎉 Graph generation completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()