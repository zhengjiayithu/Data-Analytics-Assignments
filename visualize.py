from os.path import dirname, join

import numpy as np
import pandas as pd
import datetime as dt

from bokeh.plotting import figure, show, output_file, vplot
from bokeh.layouts import layout, widgetbox, row
from bokeh.models import ColumnDataSource, HoverTool, Div
from bokeh.models.widgets import Slider, Select
from bokeh.io import curdoc


business = pd.read_csv("Montreal.csv",encoding = "latin1")
user = pd.read_csv("user.csv")
review = pd.read_csv("review.csv")

user["yelping_since"]=pd.to_datetime(user["yelping_since"])
user["stars"] = user["average_stars"]
review["date"]=pd.to_datetime(review["date"])
user["year"]=user["yelping_since"].dt.year
review["review_len"] = [len(t) for t in review["text"]]
review["year"] = review["date"].dt.year

business["neighbordata"] = business["neighborhoods"]
business["neighbordata"] = [i.strip('[]').strip("''") for i in business["neighbordata"]]
business["neighbordata"] = [i.replace('\\xe9', str("\xe9")) for i in business["neighbordata"]]
business["neighbordata"] = [i.replace("u'", "") for i in business["neighbordata"]]
business["neighbordata"] = [i.replace("\\xe8", str("\xe8")) for i in business["neighbordata"]]
business["neighbordata"] = [i.replace("\\xf4", str("\xf4")) for i in business["neighbordata"]]
business["neighbordata"] = [i.replace("\\xe2", str("\xe2")) for i in business["neighbordata"]]
business["neighbordata"] = [i.replace("\\u", "") for i in business["neighbordata"]]

neighbors = list(business["neighbordata"].unique())
neighbors.append("All")

alldata = {"Restaurants":business, "Users":user, "Reviews":review}

axis_map = {
    "Stars": "stars",
    "Review Count": "review_count"}


desc = Div(text=open(join(dirname(__file__), "description.html")).read(), width=800)

# Create Input controls
data = Select(title="Dataset", value="Restaurants",
               options=["Restaurants","Users","Reviews"])

review_count = Slider(title="Minimum Number of Reviews", value=50, start=0, end=600, step=30)
stars = Slider(title="Minimum Stars", value=1, start=0, end=5, step=0.5)

# For restaurants
neighborhoods = Select(title="Neighborhoods", value="All",
               options=neighbors)

# For users & reviews
min_year = Slider(title="Begin Year", start=2004, end=2016, value=2007, step=1)
max_year = Slider(title="End Year", start=2004, end=2016, value=2016, step=1)

# For reviews
length = Slider(title="Minimum Length of Review Texts", value=0, start=0, end=600, step=30)

x_axis = Select(title="X Axis", options=["Stars","Review Count"], value="Stars")

# Create Column Data Source that will be used by the plot
source = ColumnDataSource(data=dict(x=[], y=[])) 

# p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None, tools=[hover])
# p.circle(x="x", y="y", source=source, size=7, color="color", line_color=None, fill_alpha="alpha")
p = figure(plot_height=600, plot_width=700, title="", toolbar_location=None)
p.quad(top="top", bottom=0, left="left", right="right",source=source,fill_color="#99d8c9", fill_alpha=0.8)

def select_data():
    dataname = data.value
    data_use = alldata[dataname]
    if dataname == "Restaurants":
        selected = data_use[(data_use["review_count"]>=review_count.value) &
            (data_use["stars"]>=stars.value)]
        if (neighborhoods.value != "All"):
            selected = selected[selected["neighbordata"]==neighborhoods.value]
    elif dataname == "Users":
        selected = data_use[(data_use["year"]>=min_year.value) & (data_use["year"]<=max_year.value) &
            (data_use["stars"]>=stars.value) &
            (data_use["review_count"]>=review_count.value)]
    else:
        selected = data_use[(data_use["year"]>=min_year.value) & (data_use["year"]<=max_year.value) &
            (data_use["stars"]>=stars.value) &
            (data_use["review_len"]>=length.value)]
    return selected

def update():
    df = select_data()
 
    x_name = axis_map[x_axis.value]
 
    measured = df[x_name]
    hist, edges = np.histogram(measured, density=True, bins=20)
 
    p.xaxis.axis_label = x_axis.value
    p.yaxis.axis_label = "Distribution"
    p.title.text = "Dataset {} Selected".format(data.value)
    source.data = dict(
        top=hist,
        left=edges[:-1],
        right=edges[1:]
    )

controls = [data, stars, review_count, neighborhoods, min_year, max_year, length, x_axis]

for control in controls:
    control.on_change('value', lambda attr, old, new: update())

sizing_mode = 'fixed'  # 'scale_width'

inputs = widgetbox(*controls, sizing_mode=sizing_mode)
l = layout([
    [desc],
    [inputs, p],
], sizing_mode=sizing_mode)

update()  # initial load of the data

curdoc().add_root(l)
curdoc().title = "Data Overview"
