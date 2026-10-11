from http.client import NON_AUTHORITATIVE_INFORMATION
from flask import Flask, request,session,redirect,render_template,url_for,flash,make_response
import hashlib
import sympy as sp
from sympy import limit,oo,sqrt
import sqlite3
from datetime import timedelta
import secrets  
import io
from dotenv import load_dotenv
import re
import html
import base64
import os
from threading import Thread
from datetime import datetime
import smtplib
import random
import ssl

pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
patter1=r'^[a-zA-Z]+[0-9]{8,}$'
load_dotenv()
app=Flask(__name__)
app.config["SESSION_SECURE"]=True
app.config["SESSION_HTTPONLY"]=True
app.config["PERMANENT_SESSION_LIFETIME"]=timedelta(days=396)
app.config["SECRET_KEY"]=os.getenv("key")

def seldefine():
    return secrets.token_hex()


def init():
    session["life"]=3
    session["idpage"]=1
    session['idpage_dr']=1
    session['continuite']=1
    session['asymptote']=1
    session['variation']=1
    session['regen']=None
    session['regen_rea']=None
    session["statut"]="not_register"
    

def has(chaine):
    hashobj=hashlib.sha256(chaine.encode())
    chainehash=hashobj.hexdigest()
    return str(chainehash)

   
@app.route("/")
def main():
    session.permanent=True
    if "idpage" in session:
        return render_template("main.html")
    else:
        init()
        return render_template("main.html")


@app.route("/sign-up",methods=["get"])
def sin():
    if  session['statut']=="register":
        return redirect(url_for('main'))
    else:
        return render_template("signup.html")

@app.route("/verification",methods=["post"])
def verif():
    name=request.form.get("username")
    Email=request.form.get("email")
    mdp=request.form.get('password')
    if not re.match(pattern,Email):
        return render_template('signup.html')
    code=random.randint(100000,999999)
    session['code']=code
    sender='bonanmaths@gmail.com'
    password="wgek asgb bggg fexi"
    message=f"""\
FROM:{sender}
To:{Email}
Subject:code de verification
Content-Type: text/html
<html>
  <body style="font-family: Arial, sans-serif; background-color: #f3f3f3; padding: 20px;">
    <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 12px; padding: 30px; box-shadow: 0 0 15px rgba(122, 71, 145, 0.3);">
      <h2 style="color: #7a4791; margin-bottom: 20px;">Bonjour {name},</h2>
      <p style="font-size: 16px; color: #333;">
        Voici votre <strong style="color: #7a4791;">code de verification</strong> : <span style="font-weight: bold; font-size: 18px;">{code}</span><br />
        pour vous connecter a <a href="https://bonanlearn.online" style="color: #7a4791; text-decoration: none;">bonnalearn.com</a>.
      </p>
      <p style="font-size: 14px; color: #555;">
        Merci de votre confiance ainsi que de l'importance que vous nous  accordez .
      </p>
    </div>
  </body>
</html>
"""
    context=ssl._create_unverified_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as conn:
        conn.login(sender,password)
        conn.sendmail(sender,Email,message)
    exp=datetime.now()+timedelta(hours=12)
    Html=render_template('verif.html') 
    response=make_response(Html)  
    response.set_cookie("cookie_name",name,expires=exp,secure=True,samesite="Lax")
    response.set_cookie("cookie_email",Email,expires=exp,secure=True,samesite="Lax")
    response.set_cookie("cookie_mdp",mdp,expires=exp,secure=True,samesite="Lax")
    return response


@app.route("/verif_login",methods=['post'])
def verif_login():
    Id=request.form.get('ID')
    mdp=request.form.get('password')
    if re.match(pattern,Id):
        Email=Id
    else:
        name=Id    
    code=random.randint(100000,999999)
    session['code']=code
    sender='bonanmaths@gmail.com'
    password="wgek asgb bggg fexi"
    message=f"""\
    FROM:{sender}
    To:{Email}
Subject: code de verification
Content-Type: text/html

<html>
  <body style="font-family: Arial, sans-serif; background-color: #f3f3f3; padding: 20px;">
    <div style="max-width: 600px; margin: auto; background-color: white; border-radius: 12px; padding: 30px; box-shadow: 0 0 15px rgba(122, 71, 145, 0.3);">
      <h2 style="color: #7a4791; margin-bottom: 20px;">Bonjour {Id},</h2>
      <p style="font-size: 16px; color: #333;">
        Voici votre <strong style="color: #7a4791;">code de verification</strong> : <span style="font-weight: bold; font-size: 18px;">{code}</span><br />
        pour vous connecter a <a href="https://bonanlearn.com" style="color: #7a4791; text-decoration: none;">bonnalearn.com</a>.
      </p>
      <p style="font-size: 14px; color: #555;">
        Merci de votre confiance ainsi que de l'importance que vous nous  accordez .
      </p>
    </div>
  </body>
</html>
"""
    context=ssl._create_unverified_context()
    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as conn:
        conn.login(sender,password)
        conn.sendmail(sender,Email,message)
    exp=datetime.now()+timedelta(hours=12)
    Html=render_template('verif_log.html') 
    response=make_response(Html)  
    response.set_cookie("cookie_ID",Id,expires=exp,secure=True,samesite="Lax")
    response.set_cookie("cookie_mdp_lo",mdp,expires=exp,secure=True,samesite="Lax")
    return response




@app.route("/trsign-up",methods=["post"])
def tr():
    conn=sqlite3.connect("data.db")
    curseur=conn.cursor()
    req="insert into users(username,Email,password,sel) values(?,?,?,?)"
    code=int(request.form.get("verif"))
    code_verification=session["code"]
    if code==code_verification:
        name=request.cookies.get('cookie_name')
        Email=request.cookies.get('cookie_email')
        mdp=request.cookies.get('cookie_mdp')
    else:
        return redirect(url_for("sin"))    
    if re.match(pattern,Email):
        sel=seldefine()
        Mdp=mdp+sel 
        mdpsecure=has(Mdp)
        while True:    
            try:
                curseur.execute(req,(name,Email,mdpsecure,sel))
                c=3
                if c:
                    c=0
                    break
            except sqlite3.IntegrityError:
                er="Erreur lié a l'intégrité ou au doublon"
                return render_template('signup.html')
        conn.commit()
        conn.close() 
        Name=has(name)
        session['statut']='register'
        return render_template("main.html")
    else:
        return render_template("signup.html")
    
    
    

    

@app.route("/login")
def login():
    s=session['statut']
    if s=="register":
        return redirect(url_for('main'))
    else: return render_template('login.html')

@app.route("/trlogin",methods=["post"])
def trlogin():
    code=int(request.form.get("code_verif"))
    Code=int(session['code'])
    message="information incorrecte"
    if not code==Code:
        render_template("login.html",message=message)
    Id=request.cookies.get('cookie_ID')
    print(Id)
    mdp=request.cookies.get('cookie_mdp_lo')
    conn=sqlite3.connect('data.db')
    curseur=conn.cursor()
    if re.match(pattern,Id):   
        req="select password,sel from users where Email=?"
        curseur.execute(req,(Id,))
        expr_final=curseur.fetchall()
        Answer=expr_final[0]
        m_dp=Answer[0]
        sel=Answer[1]
        Mdp=mdp+sel
        Mpd=has(Mdp)
        if Mpd==m_dp:
            session["statut"]="register"
            return render_template("main.html")
        else: 
            return render_template("login.html")
    else:
        req="select password,sel from users where username=?"
        curseur.execute(req,(Id,))
        expr_final=curseur.fetchall()
        Answer=expr_final[0]
        m_dp=Answer[0]
        sel=Answer[1]
        Mdp=mdp+sel
        Mpd=has(Mdp)
        if Mpd==m_dp:
            session["statut"]='register'

            return render_template("main.html")
        else: 
            return render_template("login.html")
 

@app.route('/logout')
def logout():
    session.clear()
    init()    
    return redirect(url_for("login"))
 
@app.route('/mainlim')
def mainlim():
     return render_template('mainlim.html')

@app.route('/trmainlim',methods=["post"])
def trmainlim():
    if request.form.get("action")=='racine_limite':
        expr=request.form.get('expressionlim')
        rcarré="\u221A()"
        Expre=expr+rcarré
        return render_template("mainlim.html",a=Expre)
    x,y=sp.symbols("x,y")
    
    expr=request.form.get("expressionlim")
    if "\u221A" in expr:
        expr_final=expr.replace("\u221A","sqrt")
        expr_final=sp.sympify(expr_final)
        expr_final=sp.factor(expr_final)
        variable=request.form.get("variable")
        valeur=request.form.get("valeur")
        Sens=request.form.get('sens')
        if Sens =='':
            limite=limit(expr_final,variable,valeur)
            Limite=str(limite)
            
            if "sqrt" in Limite:
                Limite=Limite.replace("sqrt","\u221A")
            return render_template('answers.html',an=Limite,E=expr_final,i=variable,v=valeur)
        else:
            limite=limit(expr_final,variable,valeur,Sens)
            return render_template("answers.html",an=limite,E=expr_final,i=variable,v=valeur)
    else:
        expr_not_racine=request.form.get("expressionlim")
        Expr_not_racine=sp.sympify(expr_not_racine)
        Expr_not_racine=sp.factor(Expr_not_racine)
        valeur_not_racine=request.form.get('valeur')
        sens_not_racine=request.form.get('sens')
        variable_not_racine=request.form.get("variable")
        if sens_not_racine=='':
            limite_not_racine=limit(Expr_not_racine,variable_not_racine,valeur_not_racine)
            limite_not_racine=str(limite_not_racine)
            if "sqrt" in limite_not_racine:
                Limite_not_racine=limite_not_racine.replace("sqrt","\u221A")
                return render_template("answers.html",E=Expr_not_racine,an=Limite_not_racine,i=variable_not_racine,v=valeur_not_racine)
            else:
                return render_template("answers.html",E=Expr_not_racine,an=limite_not_racine,i=variable_not_racine,v=valeur_not_racine)

        else:
            if "sqrt" in limite_not_racine:
                Limite_not_racine=limite_not_racine.replace("sqrt","\u221A")
                return render_template("answers.html",E=Expr_not_racine,an=Limite_not_racine)
            limite_not_racine=limit(Expr_not_racine,variable_not_racine,valeur_not_racine,sens_not_racine)
            return render_template("answers.html",E=Expr_not_racine,an=Limite_not_racine)

@app.route("/main_derivation")
def derivation():
    return render_template("derivation.html")

@app.route("/trmain_derivation",methods=["post"])
def trmain_derivation():
    if request.form.get("action")=="racine_der":
        expr=request.form.get('der')
        rcarré="\u221A()"
        Expre=expr+rcarré
        return render_template("derivation.html",a=Expre)
    else:
        x,y=sp.symbols("x,y")
        expr=request.form.get("der")
        variable=request.form.get("variable")
        dr=sp.diff(expr,variable)
        return render_template("answers.html",an=dr)
    
@app.route("/recup")
def recup():
    future=datetime.now()+timedelta(minutes=43)
    Future=future.timestamp()
    session['regen_rea']=future
    session['regen']=int(Future)
    return render_template("vide.html")

@app.route("/cours_lim")
def cours_lim():
    sta=request.args.get('reponse')
    life=session["life"]
    if life==0:
        if not session['regen']==None:
            h=session["regen"]
            ver=session['regen_rea']
            H=int(datetime.now().timestamp())
            temps_restant=h-H
            if temps_restant <=0:
                session["life"]+=1
                session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                session['regen_rea']=ver+timedelta(minutes=43)
                return redirect(url_for('cours_lim'))
            else:
                return render_template("vide.html",t=temps_restant) 
        else:  
            return redirect(url_for("recup"))
    elif life <3 :
        if not session['regen']==None:
            régen=session["regen"]
            ver=session['regen_rea']
            now=int(datetime.now().timestamp())
            if now>=régen: 
                session["life"]+=1
                if session['life']<3:
                    session['regen_rea']=ver+timedelta(minutes=43)
                    session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                    
        else:
            return redirect(url_for('recup')) 
        
    if session['life']==3:      
        session['regen']=None
        session['regen_rea']=None
    n=session["idpage"]
    if n==19:
        session["idpage"]=1
        return render_template('fin.html')
    conn=sqlite3.connect("quiz.db")
    curseur=conn.cursor()
    req='select pages,ANSWER from quiz where id=?'
    curseur.execute(req,(n,))
    v=curseur.fetchone()
    page=v[0]
    return render_template("courlim.html",k=page,progress=n,l=life,reponse=sta)

@app.route("/next")
def next():
    session['idpage']+=1
    Reponse=request.args.get('reponse')
    return redirect(url_for('cours_lim',reponse=Reponse))

@app.route('/next_dr')
def next_dr():
    Reponse=request.args.get('reponse')
    session['idpage_dr']+=1
    return redirect(url_for('cours_der',reponse=Reponse))

@app.route("/trcours_lim",methods=["post"])
def trcours_lim():
    n=session['idpage']
    answer_li=request.form.getlist("reponse")
    repo_lengh=len(answer_li)
    conn=sqlite3.connect("quiz.db")
    curseur=conn.cursor()
    c=0
    req="select pages,ANSWER from quiz where id=?"
    curseur.execute(req,(n,))
    result=curseur.fetchone()
    Page=result[0]
    reponse_quiz=str(result[1]).split(",")
    reponse_quiz_length=len(reponse_quiz)
    if reponse_quiz_length==repo_lengh:
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('next',reponse="1"))
        else:
            session["life"]-=1
            return redirect(url_for('cours_lim',reponse="0"))
    else:
        reponse_quiz=str(result[1]).split(",")
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('cours_lim'))
        else:
            session["life"]-=1
            return redirect(url_for('cours_lim',reponse="0"))


@app.route("/cours_der")
def cours_der():
    sat=request.args.get('reponse')
    life=session["life"]
    if life==0:
        if not session['regen']==None:
            h=session["regen"]
            ver=session['regen_rea']
            H=int(datetime.now().timestamp())
            temps_restant=h-H
            if temps_restant <=0:
                session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                session['regen_rea']=ver+timedelta(minutes=43)
                session["life"]+=1
                return redirect(url_for('cours_lim'))
            else:
                return render_template("vide.html",temps_restant=temps_restant) 
        else:  
            return redirect(url_for("recup"))
    elif life <3 :
        if not session["regen"]==None:
            régen=session["regen"]
            ver=session['regen_rea']
            now=int(datetime.now().timestamp())
            if now>=régen:
                if session['life']<3:
                    session['regen_rea']=ver+timedelta(minutes=43)
                    session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                session["life"]+=1
        else:
            return redirect(url_for('recup'))   
   
    n=session["idpage_dr"]
    if session['life']==3:
        session['regen']=None
        session['regen_rea']=None
    if n==14:
        session["idpage_dr"]=1
        return render_template("fin_dr.html")
    conn=sqlite3.connect("quiz_dr.db")
    curseur=conn.cursor()
    req='select PAGE from quiz where id=?'
    curseur.execute(req,(n,))
    v=curseur.fetchone()
    page=v[0]
    return render_template("courder.html",k=page,l=life,progress=n,reponse=sat)

@app.route("/trcours_dr",methods=["post"])
def trcours_dr():
    n=session['idpage_dr']
    answer_li=request.form.getlist("reponse")
    repo_lengh=len(answer_li)
    conn=sqlite3.connect("quiz_dr.db")
    curseur=conn.cursor()
    c=0
    req="select PAGE,ANSWER from quiz where id=?"
    curseur.execute(req,(n,))
    result=curseur.fetchone()
    Page=result[0]
    reponse_quiz=str(result[1]).split(",")
    reponse_quiz_length=len(reponse_quiz)
    if reponse_quiz_length==repo_lengh:
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('next_dr',reponse="1"))
        else:
            session["life"]-=1
            return redirect(url_for('cours_der',reponse='0'))
    else:
        session["life"]-=1
        return redirect(url_for('cours_der',reponse='0'))



@app.route("/back")
def backscape():
    niv=session["idpage"]
    if niv==1:
        return redirect(url_for('cours_lim'))
    session['idpage']-=1
    return redirect(url_for('cours_lim'))

@app.route("/back_dr")
def backscape_dr():
    niv=session["idpage_dr"]
    if niv==1:
        return redirect(url_for('cours_der'))
    session['idpage_dr']-=1
    return redirect(url_for('cours_der'))

@app.route("/continuité")
def continuité():
    sta=request.args.get('reponse')
    life=session["life"]
    if life==0:
        if not session['regen']==None:
            h=session["regen"]
            H=int(datetime.now().timestamp())
            ver=session['regen_rea']
            temps_restant=h-H
            if temps_restant <=0:
                session["life"]+=1
                session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                session['regen_rea']=ver+timedelta(minutes=43)
                return redirect(url_for('continuité'))
            else:
                return render_template("vide.html",temps_restant=temps_restant) 
        else:  
            return redirect(url_for("recup"))
    elif life <3 :
        if not session["regen"]==None:
            régen=session["regen"]
            now=int(datetime.now().timestamp())
            if now>=régen:
                ver=session['regen_rea']
                if session['life']<3:
                    session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                    session['regen_rea']=ver+timedelta(minutes=43)
                session["life"]+=1
        else:
            return redirect(url_for('recup'))   
   
    n=session["continuite"]
    if session['life']==3:
        session['regen']=None
        session['regen_rea']=None
    if n==10:
        session["continuite"]=1
        return render_template("fin_cont.html")
    conn=sqlite3.connect("continu.db")
    curseur=conn.cursor()
    req='select page from quiz where id=?'
    curseur.execute(req,(n,))
    v=curseur.fetchone()
    page=v[0]
    return render_template("continuite.html",k=page,l=life,progress=n,reponse=sta)

@app.route('/trcontinuité',methods=['post'])
def trcontinuité():
    n=session['continuite']
    answer_li=request.form.getlist("reponse")
    repo_lengh=len(answer_li)
    conn=sqlite3.connect("continu.db")
    curseur=conn.cursor()
    c=0
    req="select page,answer from quiz where id=?"
    curseur.execute(req,(n,))
    result=curseur.fetchone()
    Page=result[0]
    reponse_quiz=str(result[1]).split(",")
    reponse_quiz_length=len(reponse_quiz)
    if reponse_quiz_length==repo_lengh:
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('next_dr',reponse="1"))
        else:
            session["life"]-=1
            return redirect(url_for('cours_der',reponse="0"))
    else:
        reponse_quiz=str(result[1].split(","))
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('cours_der'))
        else:
            session["life"]-=1
            return redirect(url_for('cours_der',reponse="0"))


@app.route('/nextcont')
def next_cont():
    Reponse=request.args.get('reponse')
    session['continuite']+=1
    return redirect(url_for('continuité',reponse=Reponse))

@app.route('/backscapecont')
def backscape_cont():
    if session['continuite']==1:
        return redirect(url_for('continuité'))
    session['continuite']-=1
    return redirect(url_for('continuité'))

@app.route('/asymp')
def asymp():
    stat=request.args.get('reponse')
    life=session["life"]
    if life==0:
        if "regen" in session:
            h=session["regen"]
            ver=session['regen_rea']
            H=int(datetime.now().timestamp())
            temps_restant=h-H
            if temps_restant <=0:
                session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                session['regen_rea']=ver+timedelta(minutes=43)
                session["life"]+=1
                return redirect(url_for('asymp'))
            else:
                return render_template("vide.html",temps_restant=temps_restant) 
        else:  
            return redirect(url_for("recup"))
    elif life <3 :
        if not session["regen"]==None:
            régen=session["regen"]
            ver=session['regen_rea']
            now=int(datetime.now().timestamp())
            if now>=régen:
                if session['life']<3:
                    session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                    session['regen_rea']=ver+timedelta(minutes=43)
                session["life"]+=1
        else:
            return redirect(url_for('recup'))   
   
    n=session["asymptote"]
    if session['life']==3:
        session['regen']=None
        session['regen_rea']=None
    if n==11:
        session["asymptote"]=1
        return render_template("fin_as.html")
    conn=sqlite3.connect("asymptote.db")
    curseur=conn.cursor()
    req='select page from quiz where id=?'
    curseur.execute(req,(n,))
    v=curseur.fetchone()
    page=v[0]
    return render_template("asymptote.html",k=page,l=life,progress=n,reponse=stat)

@app.route('/trasymptote',methods=['post'])
def trasymptote():
    n=session['asymptote']
    answer_li=request.form.getlist("reponse")
    repo_lengh=len(answer_li)
    conn=sqlite3.connect("asymptote.db")
    curseur=conn.cursor()
    c=0
    req="select page,answer from quiz where id=?"
    curseur.execute(req,(n,))
    result=curseur.fetchone()
    Page=result[0]
    reponse_quiz=str(result[1]).split(",")
    reponse_quiz_length=len(reponse_quiz)
    if not answer_li:
        session['life']-=1
        return redirect(url_for('asymp',reponse='0'))
    if reponse_quiz_length==repo_lengh:
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('next_as',reponse='1'))
        else:
            session["life"]-=1
            return redirect(url_for('asymp',reponse="0"))
    else:
        reponse_quiz=str(result[1].split(","))
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('asymp'))
        else:
            session["life"]-=1
            return redirect(url_for('asymp',reponse="0"))
        
@app.route('/next_as')
def next_as():
    Reponse=request.args.get('reponse')
    session['asymptote']+=1
    return redirect(url_for('asymp',reponse=Reponse))    

@app.route('/backscape_as')
def backscape_as():
    if session['asymptote']==1:
        return redirect(url_for('asymp'))
    session['asymptote']-=1
    return redirect(url_for('asymp'))

@app.route('/variation')
def variation():
    life=session["life"]
    sta=request.args.get('reponse')
    if life==0:
        if "regen" in session:
            h=session["regen"]
            ver=session['regen_rea']
            H=int(datetime.now().timestamp())
            temps_restant=h-H
            if temps_restant <=0:
                session["life"]+=1
                session['regen_rea']=ver+timedelta(minutes=43)
                session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                return redirect(url_for('continuité'))
            else:
                return render_template("vide.html",temps_restant=temps_restant) 
        else:  
            return redirect(url_for("recup"))
    elif life <3 :
        if not session['regen']==None:
            régen=session["regen"]
            ver=session['regen_rea']
            now=int(datetime.now().timestamp())
            if now>=régen:
                if session['life']<3:
                    session['regen']=int((ver +timedelta(minutes=43)).timestamp())
                    session['regen_rea']=ver+timedelta(minutes=43)
                session["life"]+=1
        else:
            return redirect(url_for('recup'))   
   
    n=session["variation"]
    if session['life']==3:
        session['regen']=None
        session['regen_rea']=None
    if n==9:
        session["variation"]=1
        return render_template("fin_var.html")
    conn=sqlite3.connect("variation.db")
    curseur=conn.cursor()
    req='select page from quiz where id=?'
    curseur.execute(req,(n,))
    v=curseur.fetchone()
    page=v[0]
    return render_template("variation.html",k=page,l=life,progress=n,reponse=sta)


@app.route('/trvariation',methods=['post'])
def trvariation():
    n=session['variation']
    answer_li=request.form.getlist("reponse")
    repo_lengh=len(answer_li)
    conn=sqlite3.connect("variation.db")
    curseur=conn.cursor()
    c=0
    req="select page,answer from quiz where id=?"
    curseur.execute(req,(n,))
    result=curseur.fetchone()
    Page=result[0]
    reponse_quiz=str(result[1]).split(",")
    reponse_quiz_length=len(reponse_quiz)
    if reponse_quiz_length==repo_lengh:
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('next_var',reponse="1"))
        else:
            session["life"]-=1
            return redirect(url_for('variation',reponse="0"))
    else:
        reponse_quiz=str(result[1].split(","))
        for i in range(repo_lengh): 
            if reponse_quiz[i] in answer_li:
                c+=1

        if c==reponse_quiz_length:
            return redirect(url_for('variation'))
        else:
            session["life"]-=1
            return redirect(url_for('variation',reponse="0"))
        
@app.route('/next_var')
def next_var():
    Reponse=request.args.get('reponse')
    session['variation']+=1
    return redirect(url_for('variation',reponse=Reponse))

@app.route('/backscape_var')
def backscape_var():
    if session['variation']==1:
        return redirect(url_for('variation'))
    session['variation']-=1
    return redirect(url_for('variation'))


@app.route('/privacy')
def privacy():
    return render_template('politique.html')

@app.route("/cookies")
def cookies():
    return render_template('cookie.html')

@app.route('/condition')
def cond():
    return render_template('condition.html')

@app.route('/leg')
def legal():
    return render_template('leg.html')



app.run(debug=True)