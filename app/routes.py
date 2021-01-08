from flask import render_template, request
from app import app, db, sche
from app.models import Trichpush
import json

from app.tools.monitor import send_message


def get_message(mytype, message):
    return {
        "code": mytype,
        "message": message
    }


def start_it(id):
    tp = Trichpush.query.filter(Trichpush.id == id).first()
    if tp is None:
        return get_message(0, "id不存在")
    all_id = tp.rich_id
    print(all_id)
    try:
        all_id = tp.rich_id.split(",")
    except Exception as e:
        try:
            all_id = tp.rich_id.split("，")
        except Exception as e:
            print("split Chinese error")

    print(all_id)
    if tp.rich_status == '停止':
        send_message(tp.rich_code, all_id)
        tp.rich_status = "启动"
        db.session.commit()
        sche.add_job(send_message,
                     'cron',
                     day_of_week='mon-fri', hour=14, minute=30,
                     args=[tp.rich_code, all_id], id=str(tp.id),
                     end_date='2030-05-30')
        return get_message(1, "启动成功")
    return get_message(0, "启动失败")


def stop_it(id):
    tp = Trichpush.query.filter(Trichpush.id == id).first()
    if tp is None:
        return get_message(0, "id不存在")
    print(tp.rich_status)
    if tp.rich_status == '启动':
        try:
            sche.remove_job(job_id=str(id))
        except Exception as e:
            print("remove error")
        tp.rich_status = "停止"
        db.session.commit()
        return get_message(1, "停止成功")
    return get_message(0, "出现错误,不可停止")

    # send_message(each.rich_code, all_id)

    # sche.start()


@app.route('/api/init.json')
def api_init():
    with open("./app/static/api/init.json", "rb") as f:
        data = json.load(f)
    return data


@app.route('/api/new', methods=["GET"])
def api_new():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 1, type=int)
    map = []
    try:
        searchParams = request.args.get('searchParams')
        rich_data = json.loads(searchParams)
        if rich_data['rich_id'] != '':
            map.append(Trichpush.rich_id == rich_data['rich_id'])
        if rich_data['rich_name'] != '':
            map.append(Trichpush.rich_id == rich_data['rich_name'])
        if rich_data['rich_scope'] != '':
            map.append(Trichpush.rich_id == rich_data['rich_scope'])
        if rich_data['rich_code'] != '':
            map.append(Trichpush.rich_id == rich_data['rich_code'])
    except Exception as e:
        pass

    all_result = Trichpush.query.filter(*map).order_by(Trichpush.id.asc()).paginate(page=page, per_page=limit).items
    # print(dir(all_result))
    # print(all_result)
    json_data = []
    for each in all_result:
        json_data.append(each.to_json())
    return {
        "code": 0,
        "msg": "",
        "count": 1000,
        "data": json_data
    }


@app.route('/api/add', methods=["GET", "POST"])
def api_add():
    data = json.loads(request.get_data(as_text=True))
    if data['rich_id'] == '':
        return get_message(0, "监控基金号不能为空")

    tp = Trichpush.query.filter(Trichpush.rich_name == data['rich_name']).first()
    if tp is not None:
        return get_message(0, "备注已经存在,请更换")
    tp = Trichpush.query.filter(Trichpush.rich_code == data['rich_code']).first()
    if tp is not None:
        return get_message(0, "推送号码已经存在,不要使用他人的推送号码")

    tp = Trichpush(rich_id=data['rich_id'],
                   rich_code=data['rich_code'],
                   rich_name=data['rich_name'],
                   rich_scope=data['rich_scope'] if data['rich_scope'] != '' else 0.01)

    # sche.add_job(send_message(data["rich_id"], data['rich_scope']), 'cron', day_of_week='mon-fri', hour=hour,
    #                   minute=minute, end_date='2030-05-30')
    db.session.add(tp)
    db.session.commit()
    return get_message(1, "成功添加")


@app.route('/api/edit', methods=["GET", "POST"])
def api_edit():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    if data['id'] == '':
        return get_message(0, "id不能为空")
    tp = Trichpush.query.filter(Trichpush.id == data['id']).first()
    temp = Trichpush.query.filter(Trichpush.rich_name == data['rich_name']).first()
    if temp is not None:
        if temp.id != tp.id:
            return get_message(0, "不能修改为他人的备注")
    temp = Trichpush.query.filter(Trichpush.rich_code == data['rich_code']).first()
    if temp is not None:
        if temp.id != tp.id:
            return get_message(0, "不能修改为他人的推送码")
    tp.rich_id = data['rich_id']
    tp.rich_name = data['rich_name']
    tp.rich_scope = data['rich_scope']
    tp.rich_code = data['rich_code']
    db.session.commit()
    return get_message(1, "成功编辑")


@app.route('/api/delete', methods=["GET", "POST"])
def api_delete():
    data = json.loads(request.get_data(as_text=True))
    tp = Trichpush.query.filter(Trichpush.id == data['id']).first()
    if tp is None:
        return get_message(0, "id不能为空,请更换")
    db.session.delete(tp)
    db.session.commit()
    return get_message(1, "成功删除")


@app.route('/api/delete_more', methods=["GET", "POST"])
def api_delete_more():
    data = json.loads(request.get_data(as_text=True))
    for each in data:
        print(each)
        tp = Trichpush.query.filter(Trichpush.id == each['id']).first()
        db.session.delete(tp)
    db.session.commit()
    return get_message(1, "成功删除")


@app.route('/api/stop', methods=["GET", "POST"])
def api_end():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    return stop_it(data['id'])


@app.route('/api/start', methods=["GET", "POST"])
def api_start():
    data = json.loads(request.get_data(as_text=True))
    print(data)
    return start_it(data['id'])


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome-3.html')


@app.route('/table')
def table():
    return render_template('table.html')


@app.route('/edit')
def edit():
    return render_template('edit.html')


@app.route('/add')
def add():
    return render_template('add.html')
