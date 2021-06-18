import xlrd


def decode_mapping(path):
    cat_dict = {"C":[], "M1":[], "M2":[], "E1":[], "E2":[]}
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_index(0)
    for i in range(23):
        for j in range(41):
            for key in cat_dict:
                if(sh.cell_value(i, j) == key):
                  cat_dict[key].append([j+5, i+5])
    for key in cat_dict:
        print(key, len(cat_dict[key]))
    return cat_dict

def cal_count(path, wafer_dict):
    cat_dict = {"C": [], "M1": [], "M2": [], "E1": [], "E2": []}
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_index(0)
    nrows = sh.nrows
    # print(nrows)
    for i in range(nrows):
        [x, y] = [sh.cell_value(i, 0), sh.cell_value(i, 1)]
        for key in wafer_dict:
            if [int(x), int(y)] in wafer_dict[key]:
                cat_dict[key].append([x, y])
                # print(int(x), int(y))
    for key in cat_dict:
        cat_dict[key] = len(cat_dict[key])
    for key in cat_dict:
        print(key, cat_dict[key])


if __name__ == "__main__":
    wafer_map_dict = decode_mapping("C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal X 8D 512G\\wafer.xlsx")
    cal_count("C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal X 8D 512G\\xy.xlsx", wafer_dict=wafer_map_dict)