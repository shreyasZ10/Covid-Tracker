import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, request, render_template, session, redirect, Response
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import urllib,base64
# plt.switch_backend('Qt4Agg')
matplotlib.use('Agg')
plt.style.use('fivethirtyeight')

app = Flask(__name__)

def read_data():
    df = pd.read_json('https://www.mohfw.gov.in/data/datanew.json')
    df = df.iloc[:-1, :]
    columns = [column for column in df.columns if column != 'sno']
    df = df[columns]
    df.sort_values(by = ['active'], inplace=True, ascending=False)
    df['State_name'] = df.apply(lambda x: x['state_name'] +" "+f"({x['state_code']})", axis = 1)

    df.drop(['state_name', 'state_code', 'new_active', 'new_positive','new_cured', 'new_death'], inplace = True, axis = 1)
    first_col = df.pop('State_name')
    df.insert(0, 'State_name', first_col)
    df.rename(columns={'State_name':'State Name (State Code)',
                    'active':'Active',
                    'positive':'Positive',
                    'cured':'Cured',
                    'death':'Death',
                    'new_active':'New Active',
                    'new_positive':'New Positive',
                    'new_cured':'New Cured',
                    'new_death':'New Death',
                    'state_code':'State Code'}, inplace = True)
    return df




@app.route('/', methods=("POST", "GET"))
def html_table():
    df = read_data()
    return render_template('index.html',  tables=[df.to_html(classes='data', header="true", index = False)])

@app.route('/charts', methods=("POST", "GET"))
def charts():
    df = pd.read_json('https://www.mohfw.gov.in/data/datanew.json')
    df=df.iloc[:-1,1:]
    total_states = np.arange(len(df['state_name']))
    plt.figure(num=None, figsize=(15, 12), dpi=50, facecolor='w', edgecolor='k')
    plt.barh(total_states,df['positive'], align='edge', alpha=0.5, color=(1,0,0), edgecolor=(0.5,0.2,0.8))
    plt.yticks(total_states, df['state_name'])  
    plt.xlim(1,max(df['positive'])+100) 
    plt.xlabel('Positive Number of Cases (in lakhs)')  
    plt.title('Corona Virus Cases')
    plt.ylabel('State Name')
    plt.grid(b=None)  
    plt.tight_layout()
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    plt.figure(num=None, figsize=(15, 12), dpi=50, facecolor='w', edgecolor='k')
    plt.barh(total_states,df['new_active'], align='center', alpha=0.5, color=(1,0.5,0), edgecolor=(0.5,0.4,0.8)  )
    plt.yticks(total_states, df['state_name'])  
    plt.xlim(1,max(df['new_active'])+10) 
    plt.xlabel('Active Number of Cases')  
    plt.title('Corona Virus Cases')
    plt.ylabel('State Name')
    plt.grid(b=None)
    plt.tight_layout()
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    image1 = urllib.parse.quote(string)  

    plt.figure(num=None, figsize=(15, 12), dpi=50, facecolor='w', edgecolor='k')
    plt.barh(total_states,df['death'], align='center', alpha=0.5, color=(0,0,1), edgecolor=(0.5,0.4,0.8)  )
    plt.yticks(total_states, df['state_name'])  
    plt.xlim(1,max(df['death'])+10) 
    plt.xlabel('Death Number of Cases')  
    plt.title('Corona Virus Cases') 
    plt.ylabel('State Name')
    plt.grid(b=None) 
    plt.tight_layout()
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    image2 = urllib.parse.quote(string)

    df = pd.read_json('https://www.mohfw.gov.in/data/datanew.json')
    df=df.iloc[:-1,1:]
    df = df[['state_name', 'active', 'positive', 'cured', 'death']]
    df=df.set_index('state_name',drop=True)
    df.plot.barh(stacked=True,figsize=(16,13))
    plt.grid(b=None)
    plt.ylabel('State Name')
    plt.xlabel('Distribution of Cases (in Lakhs)')
    plt.tight_layout()
    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf,format='png', dpi = 50)
    buf.seek(0)
    string = base64.b64encode(buf.read())
    image3 = urllib.parse.quote(string)
    
    return render_template('charts.html', data = uri, image1 = image1, image2 = image2, image3 = image3)
    


if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD']=True
    app.run(debug=True,use_reloader=True)