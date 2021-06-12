import re
import os
from extract_lot_number import extract_lot
import xlsxwriter


def extract_wxy(lot_list, main_path, sh_folder_list):
    wb = xlsxwriter.Workbook(main_path + "\\results.xlsx")
    sheet = wb.add_worksheet("raw data")
    total_count_for_all_lot = 0
    try:
        for each_lot in lot_list:
            match_flag = 0
            for each_sh_folder in sh_folder_list:
                # find the sh log folder for this lot
                match_res = re.match(each_lot, each_sh_folder)
                if match_res:
                    match_flag = 1
                    print("!!!!!!!!!!!!Find the SH datalog folder for lot: %s!!!!!!!!!!!!!" % match_res.group(0))
                    # print("start parsing tb__869......")
                    sh_log_path = main_path + '\\' + each_sh_folder
                    sh_log_list = os.listdir(sh_log_path)
                    pattern = re.compile(r".*?(DUT\d) (CHANNEL\d) (CHIP\d) (PLANE\d+) TB869 FAILBLOCK 0x\d")
                    for each_site in sh_log_list:
                        tb__869_dict = {}
                        tb__869_detect = 0
                        with open(sh_log_path + "\\" + each_site, "r") as f:
                            for log in f:
                                # log = f.readline()
                                match_869 = re.match(pattern, log)
                                if match_869:
                                    tb__869_detect = 1
                                    [dut, channel, chip, plane] = [match_869.group(1), match_869.group(2), match_869.group(3), match_869.group(4)]
                                    # print(log)
                                    print(each_site)
                                    print("Find fail die: ",dut, channel, chip, plane)
                                    key = "_".join([dut, channel, chip])
                                    # print(match_869.group(0))
                                    if key not in tb__869_dict:
                                        # same dut/channel/chip from different touchdown in same site share same key
                                        tb__869_dict[key] = []

                                if tb__869_detect:
                                    # DUT01 CHANNEL2   CHIP01		17		11		08		DP1584825
                                    wxyl_pattern = re.compile(r".*DUT0%s %s {3}(CHIP0%s)		(\d+)		(\d+)		"
                                                              r"(\d+)		([0-9A-Z]{9,10})"
                                                              % (dut[3:], channel, chip[4:]))
                                    wxyl_match = re.match(wxyl_pattern, log)
                                    if wxyl_match:
                                        print("find matched wxy of fail die")
                                        [c, w, x, y, l] = [wxyl_match.group(1), wxyl_match.group(2), wxyl_match.group(3),
                                                           wxyl_match.group(4), wxyl_match.group(5)]
                                        tb__869_dict[key].append([c, w, x, y, l])
                                        tb__869_detect = 0
                        # print(each_site)
                        # write dict for each site
                        if tb__869_dict:

                            print(tb__869_dict)
                            for dut_channel_chip in tb__869_dict:
                                for i in range(len(tb__869_dict[dut_channel_chip])):

                                    sheet.write(total_count_for_all_lot+i, 0, each_site)
                                    sheet.write(total_count_for_all_lot+i, 1, dut_channel_chip)
                                    sheet.write(total_count_for_all_lot+i, 2, "-".join(tb__869_dict[dut_channel_chip][i]))
                                total_count_for_all_lot += len(tb__869_dict[dut_channel_chip])
            # save when all log folders finish


            if not match_flag:
                if len(each_lot) < 13:
                    each_lot = each_lot.zfill(13)
                # print("No folder for %s, no 553 failure so log isn't downloaded" % each_lot)
        wb.close()

    except:
        wb.close()

if __name__ == "__main__":
    # file contains source code from npi express that contains all the lots
    path = "C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal X\\cal x.txt"
    # get all the lots
    all_lot_list = extract_lot(path)
    main_dir = 'C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal X'
    # log folder list downloaded, according to redshift, only 553 fail lots are downloaded
    log_folder_list = os.listdir(main_dir)
    extract_wxy(lot_list=all_lot_list, main_path=main_dir, sh_folder_list=log_folder_list)
