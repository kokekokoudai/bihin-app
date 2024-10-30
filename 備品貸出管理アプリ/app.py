from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime
import logging

app = Flask(__name__)

# ログの設定
logging.basicConfig(filename='loan_records.log', level=logging.INFO, 
                    format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# 備品リストを種別ごとに定義
items = {
    "工具類": [
        {"id": 1, "name": "ノートPC", "status": "available", "image": "laptop.jpg", "quantity": 10},
        {"id": 2, "name": "プロジェクター", "status": "available", "image": "projector.jpg", "quantity": 5},
    ],
    "塗料類": [
        {"id": 3, "name": "ホワイトボード", "status": "available", "image": "whiteboard.jpg", "quantity": 3},
        {"id": 4, "name": "マーカー", "status": "available", "image": "marker.jpg", "quantity": 20},
    ],
    "接着類":[
        {"id":5, "name":"木工用ボンド", "status":"available", "image":"bond.jpg", "quantity":10}
    ],
}

# 担当者リスト
staff_members = ["山田太郎", "佐藤花子", "鈴木一郎", "田中美咲"]

# 貸出記録
loan_records = []

@app.route('/')
def index():
    return render_template('index.html', items=items, staff_members=staff_members)

@app.route('/get_items', methods=['POST'])
def get_items():
    category = request.form['category']
    return jsonify(items[category])

@app.route('/loan', methods=['POST'])
def loan():
    item_id = int(request.form['item_id'])
    staff = request.form['staff']
    quantity = int(request.form['quantity'])
    grade = int(request.form['grade'])
    class_num = int(request.form['class'])
    loan_date = request.form['loan_date']
    notes = request.form['notes']

    # 貸出記録を追加
    loan_record = {
        'item_id': item_id,
        'item_name': next(item['name'] for category in items.values() for item in category if item['id'] == item_id),
        'staff': staff,
        'quantity': quantity,
        'grade': grade,
        'class': class_num,
        'loan_date': loan_date,
        'notes': notes,
        'type': 'loan'
    }
    loan_records.append(loan_record)

    # ログに記録
    log_message = f"貸出: 備品名: {loan_record['item_name']}, 個数: {quantity}, 担当者: {staff}, 学年クラス: {grade}-{class_num}, 日時: {loan_date}"
    logging.info(log_message)

    # 備品の在庫を更新
    for category in items.values():
        for item in category:
            if item['id'] == item_id:
                item['quantity'] -= quantity
                if item['quantity'] <= 0:
                    item['status'] = 'lent'
                break

    return redirect(url_for('index'))

@app.route('/return', methods=['POST'])
def return_item():
    item_id = int(request.form['item_id'])
    staff = request.form['staff']
    quantity = int(request.form['quantity'])
    grade = int(request.form['grade'])
    class_num = int(request.form['class'])
    return_date = request.form['return_date']
    notes = request.form['notes']

    # 返却記録を追加
    return_record = {
        'item_id': item_id,
        'item_name': next(item['name'] for category in items.values() for item in category if item['id'] == item_id),
        'staff': staff,
        'quantity': quantity,
        'grade': grade,
        'class': class_num,
        'return_date': return_date,
        'notes': notes,
        'type': 'return'
    }
    loan_records.append(return_record)

    # ログに記録
    log_message = f"返却: 備品名: {return_record['item_name']}, 個数: {quantity}, 担当者: {staff}, 学年クラス: {grade}-{class_num}, 日時: {return_date}"
    logging.info(log_message)

    # 備品の在庫を更新
    for category in items.values():
        for item in category:
            if item['id'] == item_id:
                item['quantity'] += quantity
                item['status'] = 'available'
                break

    return redirect(url_for('index'))

@app.route('/logs')
def view_logs():
    sort_by = request.args.get('sort_by', 'time')
    if sort_by == 'class':
        sorted_records = sorted(loan_records, key=lambda x: (x['grade'], x['class']))
    elif sort_by == 'item':
        sorted_records = sorted(loan_records, key=lambda x: x['item_name'])
    else:
        sorted_records = loan_records

    return render_template('logs.html', logs=sorted_records)

if __name__ == '__main__':
    app.run(debug=True)