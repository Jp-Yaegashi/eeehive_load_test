import sys

def replace_conf(device_type,environment):
    conf_path = ''
    if device_type=='SENS':
        conf_path ='./SENS/SENS.conf'
        with open(conf_path) as reader:
            content = reader.read()
        # 置換
            content = content.replace('FLEX', 'SENS')
            content = content.replace('2D', 'SENS')
        
    elif device_type=='2D':
        conf_path ='./_2D/_2D.conf'
        with open(conf_path) as reader:
            content = reader.read()
            content = content.replace('SENS', '2D')
            content = content.replace('FLEX', '2D')
    else:
        conf_path ='./FLEX/FLEX.conf'
        with open(conf_path) as reader:
            content = reader.read()
            content = content.replace('SENS', 'FLEX')
            content = content.replace('2D', 'FLEX')
    if environment=='release':#本番環境
        content = content.replace('10.17.10.2', '10.17.10.1')

    elif environment=='dev':#検証環境
        content = content.replace('10.17.10.1', '10.17.10.2')
    
    # 書き出し
    with open(conf_path, 'w') as writer:
        writer.write(content)

def replace_html(environment):
    with open('./templates/setting.html') as reader:
        content = reader.read()

    if environment=='release':#本番環境
        content = content.replace('#ffdead', '#FFFFFF')
        content = content.replace('検証環境', '本番環境')

    elif environment=='dev':#検証環境
        content = content.replace('#FFFFFF', '#ffdead')    
        content = content.replace('本番環境', '検証環境')    
    # 書き出し
    with open('./templates/setting.html', 'w') as writer:
        writer.write(content)


def main():
    args = sys.argv
    if 3 <= len(args):
        print(args[1])
        print(args[2])
        environment = args[1] #実施環境
        device_type = args[2]
        device_type = device_type.upper() #大文字へ変換
        if device_type=='SENS' or device_type=='2D' or device_type=='FLEX':
            #device_type.conf
            # 読み込み
            with open('device_type.conf') as reader:
                content = reader.read()
            if device_type=='SENS':
                # 置換
                content = content.replace('FLEX', 'SENS')
                content = content.replace('2D', 'SENS')
            elif device_type=='FLEX':
                content = content.replace('SENS', 'FLEX')
                content = content.replace('2D', 'FLEX')
            else: #2D
                content = content.replace('SENS', '2D')
                content = content.replace('FLEX', '2D')
            
            # 書き出し
            with open('device_type.conf', 'w') as writer:
                writer.write(content)

            replace_conf(device_type,environment)
            replace_html(environment)
            if environment=='release':#本番環境
                print('本番環境への適用処理完了しました')
            elif environment=='dev':#検証環境
                print('検証環境への適用処理完了しました')
            
        else:
            print('デバイスタイプ不正')
    else:
        print('パラメータエラー')

        
if __name__ == "__main__":
	main()