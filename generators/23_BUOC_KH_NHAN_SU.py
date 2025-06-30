#!/usr/bin/env python3
"""
23_BUOC_KH_NHAN_SU.py - Generate 23-step personnel plan bar chart
Uses timeline data + fixed personnel columns from image
"""

import pandas as pd
import matplotlib.pyplot as plt
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

def generate_23_buoc_nhan_su():
    """Generate the 23-step personnel plan bar chart with timeline data + fixed personnel"""
    
    # Get extracted time and calculate scaling
    extracted_time = load_extracted_time()
    target_days = extract_days_from_time(extracted_time)
    
    print(f"🎯 Target total days: {target_days}")
    
    # STEP 1: Timeline data (from 23-step process)
    timeline_csv = """Task,Base_Days
Giao nhận tài liệu và lập biên bản giao nhận tài liệu,0.5
Vận chuyển tài liệu từ kho bảo quản đến địa điểm chỉnh lý,1
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
Đưa hồ sơ vào hộp cặp,2
Viết in và dán nhãn hộp cặp,2
Vận chuyển tài liệu vào kho và xếp lên giá,1
Giao nhận tài liệu sau chỉnh lý và lập Biên bản giao nhận tài liệu,1
Nhập phiếu tin vào cơ sở dữ liệu,5
Kiểm tra chỉnh sửa việc nhập phiếu tin,1
Lập mục lục hồ sơ,4
Thống kê bó gói lập danh mục và viết thuyết minh tài liệu loại,1
Kết thúc chỉnh lý,1"""
    
    # STEP 2: Personnel data (FIXED, from your image)
    personnel_csv = """Task,Quản lý dự án,Trưởng nhóm chỉnh lý,Nhân sự chỉnh lý
Giao nhận tài liệu và lập biên bản giao nhận tài liệu,1,1,5
Vận chuyển tài liệu từ kho bảo quản đến địa điểm chỉnh lý,1,1,10
Vệ sinh sơ bộ tài liệu,1,1,10
Khảo sát và biên soạn các văn bản hướng dẫn chỉnh lý,1,1,2
Phân loại tài liệu theo Hướng dẫn phân loại,1,1,10
Lập hồ sơ hoặc chỉnh sửa hoàn thiện hồ sơ theo Hướng dẫn lập hồ sơ,1,1,10
Viết các trường thông tin vào phiếu tin,1,1,10
Kiểm tra chỉnh sửa hồ sơ và phiếu tin,1,1,2
Hệ thống hóa phiếu tin theo phương án phân loại,1,1,10
Hệ thống hóa hồ sơ theo phiếu tin,1,1,10
Biên mục hồ sơ,1,1,10
Kiểm tra và chỉnh sửa việc biên mục hồ sơ,1,1,2
Ghi số hồ sơ chính thức vào phiếu tin và lên bìa hồ sơ,1,1,10
Vệ sinh tài liệu tháo bỏ ghim kẹp làm phẳng và đưa tài liệu vào bìa hồ sơ,1,1,10
Đưa hồ sơ vào hộp cặp,1,1,10
Viết in và dán nhãn hộp cặp,1,1,10
Vận chuyển tài liệu vào kho và xếp lên giá,1,1,10
Giao nhận tài liệu sau chỉnh lý và lập Biên bản giao nhận tài liệu,1,1,2
Nhập phiếu tin vào cơ sở dữ liệu,1,1,10
Kiểm tra chỉnh sửa việc nhập phiếu tin,1,1,2
Lập mục lục hồ sơ,1,1,10
Thống kê bó gói lập danh mục và viết thuyết minh tài liệu loại,1,1,10
Kết thúc chỉnh lý,1,1,2"""
    
    # Load timeline data
    timeline_df = pd.read_csv(StringIO(timeline_csv))
    timeline_df.set_index('Task', inplace=True)
    
    # Load personnel data
    personnel_df = pd.read_csv(StringIO(personnel_csv))
    personnel_df.set_index('Task', inplace=True)
    
    # Calculate scaling for timeline
    base_total = timeline_df['Base_Days'].sum()  # Should be 100
    scaling_ratio = target_days / base_total
    print(f"📊 Base total: {base_total} days")
    print(f"📊 Scaling ratio: {scaling_ratio:.3f}")
    
    # Apply scaling to timeline
    timeline_df['Ngày thực hiện'] = (timeline_df['Base_Days'] * scaling_ratio).apply(lambda x: max(1, round(x)))
    scaled_total = timeline_df['Ngày thực hiện'].sum()
    print(f"📊 Scaled total: {scaled_total} days")
    
    # Combine timeline + personnel data
    df = pd.concat([timeline_df[['Ngày thực hiện']], personnel_df], axis=1)
    
    # Reorder columns to put "Ngày thực hiện" first
    column_order = ['Ngày thực hiện', 'Quản lý dự án', 'Trưởng nhóm chỉnh lý', 'Nhân sự chỉnh lý']
    df = df[column_order]

    # Wrap labels every 2 words for tighter text blocks
    def wrap_text(text, words_per_line=2):
        words = text.split()
        return '\n'.join([' '.join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)])

    wrapped_labels = [wrap_text(task, 2) for task in df.index]

    # Dynamically calculate bottom margin based on max label height
    max_lines = max(label.count('\n') + 1 for label in wrapped_labels)
    bottom_margin = 0.3 + 0.02 * max_lines  # Tune scaling factor as needed

    # Create figure with dynamic height based on number of label lines
    fig_height = 12 + 0.5 * max_lines  # Increase base height if needed
    fig, ax = plt.subplots(figsize=(26, fig_height))

    bar_plot = df.plot(kind='bar', ax=ax, width=0.55)

    # Apply improved x-axis labels
    ax.set_xticklabels(wrapped_labels, rotation=0, ha='center', fontsize=11)

    # Add data labels
    for container in ax.containers:
        for bar in container:
            height = bar.get_height()
            if height > 0:
                ax.annotate(f'{int(height)}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=10)

    # Labels, legend, and layout
    ax.set_title('KẾ HOẠCH NHÂN SỰ (23 BƯỚC)', fontsize=20)
    ax.set_ylabel('Ngày/Nhân sự', fontsize=16)
    ax.set_xlabel('', fontsize=16)
    
    # Move legend to top right
    ax.legend(title='Nhóm nhân sự', fontsize=12, loc='upper right')
    ax.yaxis.grid(True, linestyle='--', alpha=0.6)

    # Add table below the plot (no column headers)
    table_data = df.T.values
    row_labels = df.columns.tolist()

    table = plt.table(cellText=table_data,
                      rowLabels=row_labels,
                      # colLabels removed to hide column headers
                      cellLoc='center',
                      rowLoc='center',
                      loc='bottom',
                      bbox=[0.0, -bottom_margin * 0.88, 1.0, 0.2])  # Adjust as needed

    table.auto_set_font_size(False)
    table.set_fontsize(10)

    plt.subplots_adjust(left=0.05, right=0.98, top=0.93, bottom=bottom_margin)
    
    # Save to pictures folder
    batch_id = read_batch_id()
    if batch_id:
        base_dir = Path(__file__).parent.parent
        pictures_dir = base_dir / batch_id / "pictures"
        pictures_dir.mkdir(exist_ok=True)
        
        output_file = pictures_dir / "23_BUOC_KH_NHAN_SU.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"💾 Personnel chart saved: {output_file}")
    else:
        # Fallback to current directory
        plt.savefig("23_BUOC_KH_NHAN_SU.png", dpi=300, bbox_inches='tight')
        print("💾 Personnel chart saved: 23_BUOC_KH_NHAN_SU.png")
    
    plt.show()

def main():
    print("👥 23-Step Personnel Plan Generator")
    print("=" * 50)
    
    try:
        generate_23_buoc_nhan_su()
        print("\n🎉 Personnel plan generation completed!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()