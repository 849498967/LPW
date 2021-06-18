import re
import os
from extract_lot_number import extract_lot
import xlsxwriter


def extract_wxy(lot_list, main_path, sh_folder_list):
    wb = xlsxwriter.Workbook(main_path + "\\results.xlsx")
    sheet = wb.add_worksheet("raw data")
    sheet.set_column(0, 3, width=60)
    total_count_for_all_lot = 0
    no_869_fail_but_has_553_fail_flag = 0
    lot_count = 0
    # try:
    for each_lot in lot_list:
        match_flag = 0
        for each_sh_folder in sh_folder_list:
            # find the sh log folder for this lot
            match_res = re.match(each_lot, each_sh_folder)
            if match_res:
                match_flag = 1
                no_869_fail_but_has_553_fail_flag = 1
                lot_count += 1
                print(lot_count, "!!!!!!!!!!!!Find SH datalog folder for lot: %s!!!!!!!!!!!!!" % match_res.group(0))
                # print("start parsing tb__869......")
                sh_log_path = main_path + '\\' + each_sh_folder
                sh_log_list = os.listdir(sh_log_path)
                # 869 fail pattern
                pattern = re.compile(r".*?(DUT\d) (CHANNEL\d) (CHIP\d) (PLANE\d+) TB869 FAILBLOCK 0x\d+")
                # b5
                # pattern = re.compile(r".*?(DUT\d) (CHANNEL\d) (CHIP\d) (PLANE\d+) TB446 FAILBLOCK 0x\d+")
                # loop each txt file in the folder
                for each_site in sh_log_list:
                    print(each_site)
                    tb__869_dict = {}
                    tb__869_detect = 0
                    # temp save die info for 1 dut, will refresh for each die when wxy info for the dut all found
                    die_temp_list = []
                    # how many wxy is found for current dut
                    die_match_count = 0
                    with open(sh_log_path + "\\" + each_site, "r") as f:
                        touch_down = 0
                        for log in f:
                            # add touch done infomation to distinguish each die in the same touch down
                            if re.match("TEST NAME: tb__1__DC_cont_dr_SH", log):
                                touch_down += 1
                            match_869 = re.match(pattern, log)
                            if match_869:
                                # set not found flag to 0 when we got a 869 failure
                                no_869_fail_but_has_553_fail_flag = 0
                                tb__869_detect = 1
                                [dut, channel, chip, plane] = [match_869.group(1), match_869.group(2),
                                                               match_869.group(3), match_869.group(4)]

                                # if both 2 plane fail, will be added twice, so remove plane info
                                # we need to judge, if the die is already in the list (1 plane), we need to remove it
                                if [dut, channel, chip] not in die_temp_list:
                                    die_temp_list.append([dut, channel, chip])
                                # print("find fail die: ", dut, channel, chip, plane)
                                key = "_".join(["SITE"+str(touch_down), dut, channel, chip])
                                # print(key)
                                # print(match_869.group(0))
                                if key not in tb__869_dict:
                                    # same dut/channel/chip from different touchdown in same site share same key
                                    tb__869_dict[key] = []

                            if tb__869_detect:
                                # in case one dut has more than 1 failure die
                                # if more than 1 die fail in same unit, we suppose it is overkill
                                # we need to clear the list
                                # but maybe only 1 DUT has more 1 die but another DUT only has one
                                # we need to specially handle each DUT. So a better way is we match all the WXY out,
                                # even though it is a broken one, then we do the check manually in the output excel

                                # we need to add logic: only when 869 stops then we do the judge
                                # otherwise if one DUT has more than 2 dies, it will be cleared
                                # and new dies will be added again
                                # if len(die_temp_list) > 1:
                                #     print(die_temp_list)
                                #     print("find more than 1 die failed! Go to check each DUT:")
                                #     temp_dut_dict = {}
                                #     for each_die in die_temp_list:
                                #         if each_die[0] not in temp_dut_dict:
                                #             temp_dut_dict[each_die[0]] = 1
                                #         else:
                                #             temp_dut_dict[each_die[0]] += 1
                                #     for each_dut in temp_dut_dict:
                                #         print(each_dut, temp_dut_dict[each_dut])
                                #         if temp_dut_dict[each_dut] >= 2:
                                #             print(each_dut, "has more than 1 die fail, will ignore that dut")

                                for each_die in die_temp_list:
                                    [dut, channel, chip] = each_die
                                    # DUT01 CHANNEL2   CHIP01		17		11		08		DP1584825
                                    wxyl_pattern = re.compile(r".*DUT0%s %s {3}(CHIP0%s)		"
                                                              r"(.*)		(.*)		"
                                                              r"(.*)		(.*)\n"
                                                              % (dut[3:], channel, chip[4:]))
                                    wxyl_match = re.match(wxyl_pattern, log)
                                    if wxyl_match:
                                        # when find a die's wxy, count + 1
                                        die_match_count += 1
                                        # print("find wxy of fail die: %s" % "-".join(each_die))
                                        [c, w, x, y, l] = [wxyl_match.group(1), wxyl_match.group(2),
                                                           wxyl_match.group(3), wxyl_match.group(4),
                                                           wxyl_match.group(5)]
                                        key = "_".join(["SITE"+str(touch_down), dut, channel, chip])
                                        # this logic is just in case, if come into this logic, stop the flow to check
                                        if key not in tb__869_dict:
                                            # not fond wxy, but key updated in next loop, so revert touchdown back
                                            print("No WXY find!")
                                            temp = touch_down - 1
                                            temp_key = "_".join(["SITE" + str(temp), dut, channel, chip])
                                            tb__869_dict[temp_key].append(["na", "na", "na", "na", "na"])

                                        else:
                                            tb__869_dict[key].append([c, w, x, y, l])
                                        # if all dies in the dut found wxy, refresh the flags
                                        if die_match_count == len(die_temp_list):
                                            tb__869_detect = 0
                                            die_temp_list = []
                                            die_match_count = 0

                    # need to add logic here for the units that over killed for DC
                    # we need to make sure these units didn't fail in later DC test
                    # need to check the logic first
                    # write dict for each site
                    # handle the duplicated and corrupted wxy logic here
                    if tb__869_dict:
                        # print("Summary for log file %s:" % each_site)
                        for each in tb__869_dict:
                            print(each, ":", tb__869_dict[each])
                        for dut_channel_chip in tb__869_dict:
                            for i in range(len(tb__869_dict[dut_channel_chip])):
                                sheet.write(total_count_for_all_lot+i, 0, each_site)
                                sheet.write(total_count_for_all_lot+i, 1, dut_channel_chip)
                                sheet.write(total_count_for_all_lot+i, 2,
                                            "-".join(tb__869_dict[dut_channel_chip][i]))
                            total_count_for_all_lot += len(tb__869_dict[dut_channel_chip])

        # if not match_flag:
        #     if len(each_lot) < 13:
        #         each_lot = each_lot.zfill(13)
                # print("No folder for %s, no 553 failure so log isn't downloaded" % each_lot)
        if match_flag and no_869_fail_but_has_553_fail_flag == 1:
            print("has 553 fail but no 869 fail found in CSH, please check")

    # save when all log folders finish
    wb.close()
    # except Exception as parse_error:
    #     print("Error during parse")
    #     wb.close()


if __name__ == "__main__":
    # file contains source code from npi express that contains all the lots
    path = "C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal II\\cal II.txt"
    # get all the lots
    all_lot_list = extract_lot(path)
    main_dir = 'C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal II\\'
    # main_dir = 'C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal X 8D 512G\\May-June'
    # log folder list downloaded, according to redshift, only 553 fail lots are downloaded
    log_folder_list = os.listdir(main_dir)
    extract_wxy(lot_list=all_lot_list, main_path=main_dir, sh_folder_list=log_folder_list)
