__author__ = ' abhinil'

from flask import Flask, render_template, request, g
from flask import Markup
from plotly.offline import plot
from scipy.stats import uniform, norm, expon
import pandas as pd
import math
import plotly.express as px
import time


app = Flask(__name__)


def UniformDist(mean, stddev):
    sum1 = mean*2 #a+b
    variance = stddev**2
    diff1 = math.sqrt(variance*12) #b-a
    b = (sum1 + diff1)/2
    a = (sum1 - b)

    #configs
    n = 10000
    start = a
    width = b-a
    data_uniform = uniform.rvs(size=n, loc = start, scale=width)
    df = pd.DataFrame(data_uniform, columns = ['y'])
    return df

def NormalDist(mean, stddev):
    n = 10000
    data_normal = norm.rvs(size=n, loc = mean, scale=stddev)
    df = pd.DataFrame(data_normal, columns = ['y'])
    return df

def ExpDist(mean, stddev):
    lam = stddev
    e = mean - lam
    n = 10000
    data_normal = expon.rvs(size=n, loc = e, scale=lam)
    df = pd.DataFrame(data_normal, columns = ['y'])
    return df

def graph(x1, x2):
    fig = plot(px.pie(values=[x1, x2], names=["Simul Time", "Network Overhead"]), output_type='div')
    return fig
end = 0
start = 0
@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_p = lambda: ""
    g.request_time = lambda: ""
    g.request_graph = lambda x1, x2: ""
    g.st = 0
    g.nt = 0

p = 0
@app.route('/')
def DistSimul():
    return render_template('DistSimul.html')
@app.route('/result', methods = ['POST'])
def result():
    t = request.values.get('t', 0)
    time.sleep(float(t)) 

    mean = float(request.form.get('mean'))
    stddev = float(request.form.get('stddev'))
    type = request.form.get('distribution-type')

    start = time.time()

    if(type == "Uniform"):
        df = UniformDist(mean, stddev)
    elif(type == "Normal"):
        df = NormalDist(mean, stddev)
    else:
        df = ExpDist(mean, stddev)

    my_plot_div = plot(px.histogram(df, nbins=200, title = str(type)+ " distribution"), output_type='div')
    
    end = time.time()


    g.request_p = lambda: "%.5f ms" % ((time.time() - g.request_start_time - end + start)*1000)
    g.request_time = lambda: "%.5f ms" % ((time.time() - g.request_start_time)*1000)
    g.request_graph = lambda x1, x2: Markup(graph(x1, x2))

    g.st = (end- start)*1000
    g.nt = (time.time() - g.request_start_time)*1000
    return render_template('DistSimul.html', placeholder=Markup(my_plot_div), t1 = "{:.3f}".format((end- start)*1000)+" ms" , t = (end-start)*1000)



if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0', port = 4000)
