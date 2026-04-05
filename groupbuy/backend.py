#!/usr/bin/env python3
"""group.solaripple.com backend v2."""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import sqlite3, hashlib, time, uuid, csv, io
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB = '/var/www/group/group.db'
PORT = 3011

def get_db():
    conn = sqlite3.connect(DB, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = sqlite3.connect(DB, timeout=30)
    conn.execute("PRAGMA journal_mode=WAL")
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, phone TEXT UNIQUE NOT NULL, name TEXT, company TEXT, city TEXT, role TEXT DEFAULT "buyer", verified INTEGER DEFAULT 0, created_at INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS auth_tokens (token TEXT PRIMARY KEY, user_id TEXT, created_at INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS groups (id TEXT PRIMARY KEY, product_id TEXT NOT NULL, product_name TEXT, tier_qty INTEGER, tier_price INTEGER, creator_id TEXT, status TEXT DEFAULT "open", target INTEGER, joined INTEGER DEFAULT 1, created_at INTEGER, expires_at INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS participants (id TEXT PRIMARY KEY, group_id TEXT, user_id TEXT, qty INTEGER DEFAULT 1, created_at INTEGER, status TEXT DEFAULT "pending")')
    c.execute('CREATE TABLE IF NOT EXISTS sms_codes (phone TEXT PRIMARY KEY, code TEXT, created_at INTEGER, expires_at INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS partner_applications (id TEXT PRIMARY KEY, company TEXT, contact TEXT, phone TEXT, email TEXT, qualification TEXT, employees TEXT, description TEXT, status TEXT, created_at INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS investor_applications (id TEXT PRIMARY KEY, company TEXT, contact TEXT, phone TEXT, email TEXT, mode TEXT, amount TEXT, description TEXT, status TEXT, created_at INTEGER)')
    conn.commit()
    conn.close()

init_db()

def make_token(uid):
    token = hashlib.sha256(f"{uid}:{time.time()}:{uuid.uuid4().hex}".encode()).hexdigest()
    c = get_db()
    c.execute('INSERT OR REPLACE INTO auth_tokens (token, user_id, created_at) VALUES (?, ?, ?)',
              (token, uid, int(time.time())))
    c.commit()
    c.close()
    return token

def validate_token(token):
    c = get_db()
    row = c.execute('SELECT user_id FROM auth_tokens WHERE token=?', (token,)).fetchone()
    c.close()
    return row['user_id'] if row else None

@app.route('/api/auth/send_code', methods=['POST'])
def send_code():
    phone = request.json.get('phone', '').strip()
    if not phone or len(phone) < 11:
        return jsonify({'ok': False, 'error': '手机号格式错误'}), 400
    code = uuid.uuid4().hex[:6].upper()
    c = get_db()
    c.execute('INSERT OR REPLACE INTO sms_codes VALUES (?, ?, ?, ?)',
              (phone, code, int(time.time()), int(time.time()) + 300))
    c.commit()
    c.close()
    print(f"[SMS] {phone} -> {code}")
    return jsonify({'ok': True, 'code': code, 'dev_mode': True})

@app.route('/api/auth/verify', methods=['POST'])
def verify():
    phone = request.json.get('phone', '').strip()
    code = request.json.get('code', '').strip()
    name = request.json.get('name', '').strip()
    city = request.json.get('city', '').strip()
    role = request.json.get('role', 'buyer')
    c = get_db()
    row = c.execute('SELECT * FROM sms_codes WHERE phone=? AND code=? AND expires_at>?',
                    (phone, code, int(time.time()))).fetchone()
    if not row:
        return jsonify({'ok': False, 'error': '验证码错误或已过期'}), 401
    c.execute('DELETE FROM sms_codes WHERE phone=?', (phone,))
    existing = c.execute('SELECT id FROM users WHERE phone=?', (phone,)).fetchone()
    if existing:
        uid = existing['id']
        c.execute('UPDATE users SET name=?, city=? WHERE id=?', (name, city, uid))
    else:
        uid = uuid.uuid4().hex
        c.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, 1, ?)',
                  (uid, phone, name, '', city, role, int(time.time())))
    token = make_token(uid)
    c.commit()
    c.close()
    return jsonify({'ok': True, 'token': token, 'user_id': uid})

@app.route('/api/auth/me', methods=['GET'])
def me():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({'ok': False, 'error': '未登录'}), 401
    uid = validate_token(token)
    if not uid:
        return jsonify({'ok': False, 'error': 'token无效'}), 401
    c = get_db()
    user = c.execute('SELECT id,phone,name,city,role,verified FROM users WHERE id=?', (uid,)).fetchone()
    c.close()
    return jsonify({'ok': True, 'user': dict(user)}) if user else jsonify({'ok': False}), 404

PRODUCTS = [
    {'id':'p1','name':'Ripple 100kWh工商业光储系统','spec':'PCS 50kW + Bat 100kWh + 7kW充电桩×2','category':'100kWh','badge':'热门','badgeUrgent':False,'price':130000,'oldPrice':165000,'minGroup':3,'tiers':[{'qty':3,'price':117000,'discount':'10%'},{'qty':5,'price':110500,'discount':'15%'},{'qty':10,'price':104000,'discount':'20%'}],'joined':7,'target':10,'inStock':True,'endTs':int(time.time()*1000)+86400000*2},
    {'id':'p2','name':'Ripple 200kWh工商业光储系统','spec':'PCS 100kW + Bat 200kWh + 21kW充电桩×2','category':'200kWh','badge':'特惠','badgeUrgent':True,'price':243000,'oldPrice':310000,'minGroup':3,'tiers':[{'qty':3,'price':218700,'discount':'10%'},{'qty':5,'price':206550,'discount':'15%'},{'qty':10,'price':194400,'discount':'20%'}],'joined':4,'target':5,'inStock':True,'endTs':int(time.time()*1000)+86400000*5},
    {'id':'p3','name':'Ripple 500kWh大型工商业系统','spec':'PCS 200kW + Bat 500kWh + 21kW充电桩×4','category':'500kWh','badge':'旗舰','badgeUrgent':False,'price':515000,'oldPrice':680000,'minGroup':3,'tiers':[{'qty':3,'price':463500,'discount':'10%'},{'qty':5,'price':437750,'discount':'15%'},{'qty':10,'price':412000,'discount':'20%'},{'qty':20,'price':386250,'discount':'25%'}],'joined':1,'target':3,'inStock':True,'endTs':int(time.time()*1000)+86400000*7},
    {'id':'p4','name':'Ripple PCS 100kW 单机','spec':'PCS 100kW模块，可扩展','category':'PCS','badge':'灵活','badgeUrgent':False,'price':78000,'oldPrice':95000,'minGroup':5,'tiers':[{'qty':5,'price':70200,'discount':'10%'},{'qty':10,'price':66300,'discount':'15%'},{'qty':20,'price':62400,'discount':'20%'}],'joined':12,'target':20,'inStock':True,'endTs':int(time.time()*1000)+86400000*3},
]

@app.route('/api/products', methods=['GET'])
def list_products():
    return jsonify({'ok': True, 'products': PRODUCTS})

@app.route('/api/groups', methods=['GET'])
def list_groups():
    c = get_db()
    rows = c.execute('SELECT g.*, u.name as creator_name, u.city as creator_city FROM groups g LEFT JOIN users u ON g.creator_id=u.id WHERE g.status="open" ORDER BY g.created_at DESC').fetchall()
    groups = []
    for r in rows:
        d = dict(r)
        d['participants'] = [dict(p) for p in c.execute('SELECT p.*, u.name, u.city FROM participants p JOIN users u ON p.user_id=u.id WHERE p.group_id=?', (d['id'],)).fetchall()]
        groups.append(d)
    c.close()
    return jsonify({'ok': True, 'groups': groups})

@app.route('/api/groups', methods=['POST'])
def create_group():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    uid = validate_token(token)
    if not uid:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    data = request.json
    product_id = data.get('product_id')
    tier_qty = int(data.get('tier_qty', 3))
    tier_price = int(data.get('tier_price'))
    product = next((p for p in PRODUCTS if p['id'] == product_id), None)
    if not product:
        return jsonify({'ok': False, 'error': '产品不存在'}), 404
    gid = uuid.uuid4().hex
    now = int(time.time())
    c = get_db()
    c.execute('INSERT INTO groups (id,product_id,product_name,tier_qty,tier_price,creator_id,status,target,joined,created_at,expires_at) VALUES (?,?,?,?,?,?,?,?,1,?,?)',
             (gid, product_id, product['name'], tier_qty, tier_price, uid, 'open', tier_qty, now, now + 86400000*7))
    c.execute('INSERT INTO participants (id,group_id,user_id,qty,created_at,status) VALUES (?,?,?,1,?,?)',
             (uuid.uuid4().hex, gid, uid, now, 'joined'))
    c.commit()
    c.close()
    return jsonify({'ok': True, 'group_id': gid})

@app.route('/api/groups/<gid>/join', methods=['POST'])
def join_group(gid):
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    uid = validate_token(token)
    if not uid:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    data = request.json
    qty = int(data.get('qty', 1))
    c = get_db()
    grp = c.execute('SELECT * FROM groups WHERE id=? AND status=?', (gid, 'open')).fetchone()
    if not grp:
        return jsonify({'ok': False, 'error': '团不存在或已结束'}), 404
    already = c.execute('SELECT id FROM participants WHERE group_id=? AND user_id=?', (gid, uid)).fetchone()
    if already:
        return jsonify({'ok': False, 'error': '您已参与此团'}), 400
    new_joined = grp['joined'] + qty
    status = 'closed' if new_joined >= grp['target'] else 'open'
    c.execute('UPDATE groups SET joined=?, status=? WHERE id=?', (new_joined, status, gid))
    c.execute('INSERT INTO participants (id,group_id,user_id,qty,created_at,status) VALUES (?,?,?,?,?,?)',
              (uuid.uuid4().hex, gid, uid, qty, int(time.time()), 'joined'))
    c.commit()
    c.close()
    return jsonify({'ok': True, 'joined': new_joined, 'status': status})

@app.route('/api/my_groups', methods=['GET'])
def my_groups():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    uid = validate_token(token)
    if not uid:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    c = get_db()
    rows = c.execute('SELECT g.*, p.qty as my_qty, p.status as my_status FROM groups g JOIN participants p ON g.id=p.group_id WHERE p.user_id=? ORDER BY g.created_at DESC', (uid,)).fetchall()
    c.close()
    return jsonify({'ok': True, 'groups': [dict(r) for r in rows]})

@app.route('/api/admin/export', methods=['GET'])
def export_csv():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    uid = validate_token(token)
    if not uid:
        return jsonify({'ok': False, 'error': '请先登录'}), 401
    c = get_db()
    rows = c.execute('SELECT g.id, g.product_name, g.tier_qty, g.tier_price, g.status, g.joined, g.target, u.name, u.phone, u.city, p.qty, p.status as participant_status FROM groups g JOIN participants p ON g.id=p.group_id JOIN users u ON p.user_id=u.id ORDER BY g.created_at DESC').fetchall()
    c.close()
    output = io.StringIO()
    w = csv.writer(output)
    w.writerow(['团ID','产品','成团人数','单价','团状态','已报名','目标','客户姓名','手机','城市','数量','状态'])
    for r in rows:
        w.writerow([r['id'], r['product_name'], r['tier_qty'], r['tier_price'], r['status'], r['joined'], r['target'], r['name'], r['phone'], r['city'], r['qty'], r['participant_status']])
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8-sig')),
                    mimetype='text/csv', as_attachment=True,
                    download_name=f'group_buy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

# ── Partner & Investor Applications ──────────────────────────────────────────

@app.route('/api/partner/apply', methods=['POST'])
def partner_apply():
    d = request.get_json() or {}
    required = ['company', 'contact', 'phone']
    for f in required:
        if not d.get(f):
            return jsonify({'ok': False, 'error': f'缺少必填字段: {f}'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO partner_applications
        (id, company, contact, phone, email, qualification, employees, description, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)''',
        (uuid.uuid4().hex, d['company'], d['contact'], d['phone'],
         d.get('email', ''), d.get('qualification', ''),
         d.get('employees', ''), d.get('description', ''), int(time.time())))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'message': '申请已提交，我们将在24小时内联系您'})


@app.route('/api/investor/apply', methods=['POST'])
def investor_apply():
    d = request.get_json() or {}
    required = ['company', 'contact', 'phone']
    for f in required:
        if not d.get(f):
            return jsonify({'ok': False, 'error': f'缺少必填字段: {f}'}), 400
    conn = get_db()
    c = conn.cursor()
    c.execute('''INSERT INTO investor_applications
        (id, company, contact, phone, email, mode, amount, description, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)''',
        (uuid.uuid4().hex, d['company'], d['contact'], d['phone'],
         d.get('email', ''), d.get('mode', ''), d.get('amount', ''),
         d.get('description', ''), int(time.time())))
    conn.commit()
    conn.close()
    return jsonify({'ok': True, 'message': '申请已提交，我们将在24小时内联系您'})


@app.route('/api/admin/applications', methods=['GET'])
def list_applications():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not validate_token(token):
        # Allow without auth for now (admin endpoint)
        pass
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM partner_applications ORDER BY created_at DESC')
    partners = [dict(r) for r in c.fetchall()]
    c.execute('SELECT * FROM investor_applications ORDER BY created_at DESC')
    investors = [dict(r) for r in c.fetchall()]
    conn.close()
    return jsonify({'ok': True, 'partners': partners, 'investors': investors})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=PORT, debug=False)


