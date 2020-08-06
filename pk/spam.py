import pandas as pd
import pkgutil
import io

def test1():
    # 正确返回结果
    print('-' * 20, 'Test 1', '-' * 20)
    base = pkgutil.get_data('data', 'base.html')
    print(base.decode('utf-8'))

def test2():
    # 正确返回结果
    print('-' * 20, 'Test 2', '-' * 20)
    csv = pkgutil.get_data('data', 't1/test.csv')
    print(csv.decode('utf-8'))
    print("\nRead data with pandas >>>")
    df = pd.read_csv(io.BytesIO(csv))
    print(df)

def test3():
    # 返回None
    print('-' * 20, 'Test 3', '-' * 20)
    csv = pkgutil.get_data('data.t1', 'test.csv')
    print(csv)

def test4():
    # 返回None
    print('-' * 20, 'Test 4', '-' * 20)
    csv2 = pkgutil.get_data('pk', 'test2.csv')
    print(csv2)  

def test5():
    # 正确返回结果
    print('-' * 20, 'Test 5', '-' * 20)
    csv3 = pkgutil.get_data('spam', 'test2.csv')
    print(csv3.decode('utf-8'))

def test6():
    # 正确返回结果
    print('-' * 20, 'Test 6', '-' * 20)
    csv4 = pkgutil.get_data('test', 'test2.csv')
    print(csv4.decode('utf-8'))

def test7():
    # 正确返回结果
    print('-' * 20, 'Test 7', '-' * 20)
    csv5 = pkgutil.get_data('test_', 'test2.csv')
    print(csv5.decode('utf-8'))



test1()
test2()
test3()
test4()
test5()
test6()
test7()

