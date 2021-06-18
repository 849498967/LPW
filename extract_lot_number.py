import re

def extract_lot(path):
    with open(path) as f:
        html = f.read()
        # b4
        # pat = re.compile("M[0-9A-Z]{9,10}\.?[0-9A-Z]{0,2}", re.S)
        # b5
        pat = re.compile("F[0-9A-Z]{9,10}\.?[0-9A-Z]{0,2}", re.S)

        res = re.findall(pat, html)
        for lot in set(res):
            print('\'%s\'' % lot, end=',\n')
        print("Total lots: %d" % len(set(res)))
        return list(set(res))


if __name__ == '__main__':
    path = "C:\\Users\\1000277162\\Desktop\\B4 long power down issue\\Cal II\\cal II.txt"
    extract_lot(path)
