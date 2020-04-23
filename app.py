from flask import Flask, render_template,request
from flask_ngrok import run_with_ngrok
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nlppreprocess import NLP
import arxiv
import pandas as pd
# pip install pdfminer.six==20181108
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import io
from transformers import pipeline
nlp = pipeline('question-answering')
app = Flask(__name__)
obj = NLP()

run_with_ngrok(app)

@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/selection',methods=['POST'])
def selection():
    
    username = request.form['username']
    password= request.form['password']
    
    if username=='thapar' and password=='thapar':
        return render_template('selection.html')
    else :
        return render_template('login.html', warning='Please enter correct username and password')
    
@app.route('/wcloud',methods=['GET', 'POST']) 
def wcloud():
    file = open("doc.txt","r") 
    text=file.read() 
    wordcloud = WordCloud(width = 550, height = 500, 
        				background_color ='white',  
        				min_font_size = 10).generate(text) 
        
        # plot the WordCloud image					 
    plt.figure(figsize = (8, 8), facecolor = None) 
    plt.imshow(wordcloud) 
    plt.axis("off") 
    plt.tight_layout(pad = 0) 
    plt.savefig('static/images/new_plot.png')
    return render_template('wcloud.html',name = 'new_plot', url ='static/images/new_plot.png')

@app.route('/ques_ans',methods=['GET', 'POST'])
def ques_ans():
    file = open("doc.txt","r") 
    ques= request.form["ques"]
    text=file.read() 
    ans=nlp({
    'question': ques,
    'context': text})
    new=ans['answer']
   
    return render_template('qna.html',answer=new)

@app.route('/uploader',methods=['GET', 'POST']) ##called when new file is uploaded in UI
def uploader():
   if request.method == 'POST':
       
      #pdf = request.files['file']
        fp = request.files['file']
        file = open("doc.txt","wb")
        #fp = open('Business Proposal.pdf', 'rb')
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        #print(type(retstr))
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        
        page_no = 0
        for pageNumber, page in enumerate(PDFPage.get_pages(fp.stream)):
            if pageNumber==page_no :
                interpreter.process_page(page)
        
                data = retstr.getvalue()
                
                text=obj.process(data)
                file.write(text.encode('utf-8'))
                ok='file ended \n\n\n'
                file.write(ok.encode('utf-8'))
                retstr.truncate(0)
                retstr.seek(0)

            page_no += 1
        return render_template('selectprocess.html')
    
   else:
       return render_template('upload.html', warning='not uploaded')
   
    
@app.route("/find", methods=['POST'])
def find():
    #Moving forward code
    return render_template('search.html');

@app.route("/found", methods=['POST'])
def found():
    #Moving forward code
    keywords = request.form['keywords']
    noofresults = request.form['noofresults']
    noofresults = int(noofresults)

    result = arxiv.query(query=keywords,max_results=noofresults)
    data = pd.DataFrame(columns = ["Title",'Published Date','Download Link'])
    for i in range(len(result)):
        title = result[i]['title']
        arxiv_url = result[i]['arxiv_url']
        arxiv_url=arxiv_url.replace('abs','pdf')
        published = result[i]['published']
        data_tmp = pd.DataFrame({"Title":title, "Published Date":published, "Download Link":arxiv_url},index=[0])
        data = pd.concat([data,data_tmp]).reset_index(drop=True)
    return render_template('search.html',tables=[data.to_html(render_links=True,classes=['table table-bordered'])]);

@app.route("/upload/", methods=['POST'])
def upload():
    #Moving forward code
    return render_template('upload.html');
if __name__ == "__main__":
    # app.run(debug=True,use_reloader=False)
    app.run()
