# Công cụ benchmark thuật toán sắp xếp

Công cụ dòng lệnh viết bằng Python này tạo dữ liệu số nguyên ngẫu nhiên, chạy và so sánh hai thuật toán sắp xếp có tốc độ tăng trưởng khác nhau:

| Thuật toán | Thời gian trung bình / xấu nhất | Thời gian tốt nhất | Bộ nhớ phụ | Đặc điểm |
| --- | --- | --- | --- | --- |
| Insertion sort (sắp xếp chèn) | $O(n^2)$ | $O(n)$ | $O(1)$ | Sắp xếp tại chỗ; phù hợp để minh họa thuật toán bậc hai trên dữ liệu nhỏ. |
| Bottom-up merge sort (sắp xếp trộn) | $O(n \log n)$ | $O(n \log n)$ | $O(n)$ | Sắp xếp ổn định; dùng vùng đệm phụ để trộn các đoạn đã sắp xếp. |

Ngoài thời gian chạy, chương trình kiểm tra kết quả có được sắp xếp đúng hay không. Sau khi benchmark, chương trình ghi dữ liệu dạng CSV và biểu đồ SVG thang log-log để tiện phân tích.

## Yêu cầu

- Python 3.10 trở lên.
- Không cần cài thư viện bên ngoài: chương trình chỉ dùng thư viện chuẩn Python.
- Chạy lệnh từ thư mục chứa `benchmark_tool.py`, hoặc truyền đường dẫn tới tệp script.

## Cài đặt và chạy

Mở PowerShell tại thư mục dự án rồi chạy:

```powershell
python benchmark_tool.py
```

Lệnh mặc định chạy 3 lượt cho mỗi thuật toán và kích thước `100, 1000, 5000, 10000, 100000, 1000000`. Kết quả được ghi vào:

- `benchmark_results.csv` — thời gian từng thuật toán theo kích thước.
- `benchmark_results.svg` — biểu đồ log-log của thời gian trung vị.

### Ví dụ

Chạy một số kích thước nhỏ hơn, năm lượt cho mỗi cấu hình:

```powershell
python benchmark_tool.py --sizes 100,500,1000 --trials 5
```

Chọn ngưỡng tối đa cho insertion sort và lưu tệp kết quả vào thư mục `results`:

```powershell
python benchmark_tool.py --sizes 100,500,1000,5000 --max-quadratic-size 1000 --output results/run.csv
```

Chỉ đo merge sort với một triệu phần tử:

```powershell
python benchmark_tool.py --sizes 1000000 --trials 3 --algorithms merge
```

Dùng một seed khác để tạo bộ dữ liệu khác:

```powershell
python benchmark_tool.py --sizes 100,1000,10000 --seed 123
```

## Tùy chọn dòng lệnh

| Tùy chọn | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `--sizes` | `100,1000,5000,10000,100000,1000000` | Danh sách kích thước đầu vào, ngăn cách bằng dấu phẩy. Mỗi kích thước phải là số nguyên dương và không được lặp. |
| `--trials` | `3` | Số lần chạy cho mỗi thuật toán và kích thước; phải ít nhất là 1. |
| `--seed` | `42` | Seed của bộ sinh số ngẫu nhiên, giúp tái tạo cùng bộ dữ liệu khi dùng lại seed và thứ tự kích thước. |
| `--max-quadratic-size` | `5000` | Kích thước tối đa để chạy insertion sort. Thuật toán này bị đánh dấu bỏ qua nếu đầu vào lớn hơn ngưỡng; có thể đặt ngưỡng 0 để bỏ qua hoàn toàn. |
| `--output` | `benchmark_results.csv` | Đường dẫn tệp CSV. Thư mục cha được tạo nếu chưa tồn tại. |
| `--algorithms` | `insertion merge` | Chọn một hoặc cả hai thuật toán: `insertion`, `merge`. |

Chương trình từ chối số lượt nhỏ hơn 1, ngưỡng insertion sort âm, kích thước không dương hoặc danh sách kích thước trùng nhau. Tên tệp biểu đồ SVG được lấy từ `--output` bằng cách thay phần mở rộng bằng `.svg`; ví dụ `results/run.csv` tạo `results/run.svg`.

## Cách benchmark hoạt động

Với mỗi kích thước, chương trình sinh một danh sách số nguyên trong khoảng từ 0 đến nhỏ hơn `10 × n`. Cả hai thuật toán nhận bản sao của cùng một danh sách, nhờ đó việc so sánh ở cùng kích thước dựa trên cùng đầu vào. `--seed` mặc định là 42 để có thể tái lập dữ liệu.

Đồng hồ được bắt đầu ngay trước khi gọi hàm sắp xếp và dừng ngay sau khi hàm trả về. Vì vậy, các thao tác sau không nằm trong thời gian đo:

- Sinh danh sách dữ liệu.
- Sao chép danh sách đầu vào cho mỗi lượt.
- Tạo bản chuẩn bằng hàm `sorted` và so sánh để xác nhận kết quả.
- Ghi tệp CSV hoặc biểu đồ.

Chương trình báo cáo trung vị, thời gian nhỏ nhất và lớn nhất của các lượt đo. Median (trung vị) giúp giảm ảnh hưởng của một lượt bất thường do tải hệ thống. Thời gian được đo bằng `time.perf_counter()`.

Insertion sort bị bỏ qua khi kích thước vượt `--max-quadratic-size`, vì số thao tác của nó tăng xấp xỉ theo bình phương \(n\); chạy thuật toán này với hàng trăm nghìn hoặc hàng triệu phần tử có thể kéo dài rất lâu. Dòng bị bỏ qua vẫn xuất hiện trong CSV với trạng thái `skipped`, số lượt bằng 0 và ô thời gian để trống.

### Đọc kết quả

CSV có các cột:

- `algorithm`: tên thuật toán (`insertion` hoặc `merge`).
- `complexity`: độ phức tạp thời gian được gắn với thuật toán.
- `size`: số phần tử trong đầu vào.
- `trials`: số lượt đo thực tế.
- `status`: `ok` nếu đã đo, `skipped` nếu bị giới hạn kích thước.
- `median_seconds`, `min_seconds`, `max_seconds`: thời gian đo bằng giây.

Biểu đồ SVG đặt kích thước đầu vào \(n\) trên trục ngang và thời gian trung vị trên trục dọc; cả hai trục dùng thang logarit. Trên thang này, sự khác nhau giữa tốc độ tăng trưởng có thể dễ quan sát hơn khi kích thước trải dài qua nhiều bậc độ lớn. Nếu một thuật toán bị bỏ qua ở một số kích thước, biểu đồ chỉ hiển thị các điểm đã đo.

## Cơ sở phân tích độ phức tạp

### Insertion sort

Insertion sort duyệt từng phần tử và chèn nó về đúng vị trí trong đoạn đã sắp xếp ở phía trước.

- **Trường hợp tốt nhất:** đầu vào đã tăng dần; mỗi phần tử chỉ cần kiểm tra một lần, thời gian \(\Theta(n)\).
- **Trường hợp trung bình:** đầu vào ngẫu nhiên; cần dịch chuyển một số phần tử ở phía trước, thời gian \(\Theta(n^2)\).
- **Trường hợp xấu nhất:** đầu vào giảm dần; số lần so sánh và dịch chuyển xấp xỉ
  $$
  1 + 2 + \cdots + (n-1) = \frac{n(n-1)}{2},
  $$
  nên thời gian \(\Theta(n^2)\).
- **Bộ nhớ phụ:** \(\Theta(1)\), vì thuật toán sửa danh sách tại chỗ.

Với đầu vào ngẫu nhiên trong công cụ này, có thể kỳ vọng xu hướng bậc hai khi \(n\) lớn, nhưng số đo cụ thể còn phụ thuộc vào dữ liệu và máy chạy.

### Merge sort

Merge sort bottom-up bắt đầu với các đoạn đã sắp xếp dài một phần tử. Ở mỗi vòng, nó trộn các cặp đoạn để tạo các đoạn dài gấp đôi cho đến khi toàn bộ danh sách được sắp xếp.

- Có khoảng \(\lceil \log_2 n \rceil\) vòng trộn.
- Mỗi vòng xử lý tổng cộng \(n\) phần tử.
- Tổng thời gian là \(\Theta(n \log n)\) trong trường hợp tốt nhất, trung bình và xấu nhất.
- Vùng đệm phục vụ việc trộn cần \(\Theta(n)\) bộ nhớ phụ.

### So sánh khi tăng gấp đôi kích thước

Với insertion sort ở miền \(n\) lớn, nếu thời gian tăng theo \(n^2\), việc tăng \(n\) gấp đôi dự kiến làm công việc tăng khoảng \(2^2 = 4\) lần.

Với merge sort, tỉ lệ tăng trưởng lý thuyết khi tăng từ \(n\) lên \(2n\) là:
$$
\frac{2n \log_2(2n)}{n \log_2 n}
= 2\left(1 + \frac{1}{\log_2 n}\right),
$$
và tiến gần 2 khi \(n\) tăng lớn.

Đây là dự đoán về xu hướng tiệm cận, không phải cam kết thời gian chạy chính xác. Hệ số hằng, overhead của Python, cấp phát và truy cập bộ nhớ, tải máy và dữ liệu cụ thể đều ảnh hưởng kết quả. Với đầu vào nhỏ, chi phí cố định có thể lớn hơn khác biệt giữa hai thuật toán. Nên xem nhiều kích thước, chạy nhiều lượt và so sánh trung vị thay vì kết luận từ một lần đo.

## Kiểm thử

Chạy bộ kiểm thử tích hợp sẵn:

```powershell
python -m unittest -v
```

Các kiểm thử xác nhận hai thuật toán sắp xếp đúng cả dữ liệu rỗng, phần tử trùng, số âm và kích thước không phải lũy thừa của hai; đồng thời kiểm tra giới hạn bỏ qua và đầu ra CSV/SVG.
