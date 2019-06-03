
import PyQt5.uic

def main():
    fout = open('uimainwindow.py', 'w', encoding='utf8')
    fin = open('mainwindow.ui', encoding='utf8')
    PyQt5.uic.compileUi(fin, fout)
    fin.close()
    fout.close()

if __name__ == '__main__':
    main()
