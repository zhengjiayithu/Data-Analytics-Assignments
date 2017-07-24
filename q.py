from os.path import dirname, join

import pandas as pd

from bokeh.layouts import row, widgetbox
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider, Button, DataTable, TableColumn
from bokeh.io import curdoc

result = pd.read_csv("query.csv",encoding='latin1')            

source = ColumnDataSource(data=dict())

def update():
    current = result[(result['stars'] >= slider1.value)&(result['review_count'] >= slider2.value)].dropna()
    source.data = {
        'Name'        : current.name,
        'Address'     : current.full_address,
        'Stars'       : current.stars,
        'Review Count': current.review_count,
    }

slider1 = Slider(title="Stars", start=0, end=5, value=0, step=0.5)
slider2 = Slider(title="Review Count", start=0, end=max(result['review_count']), value=0, step=int(max(result['review_count'])/10))
slider1.on_change('value', lambda attr, old, new: update())
slider2.on_change('value', lambda attr, old, new: update())

button = Button(label="Download", button_type="success")
button.callback = CustomJS(args=dict(source=source),
                           code=open(join(dirname(__file__), "download.js")).read())

columns = [
    TableColumn(field="Name", title="Restaurant Name"),
    TableColumn(field="Address", title="Address"),
    TableColumn(field="Stars", title="Stars"),
    TableColumn(field="Review Count", title="Review Count")
]

data_table = DataTable(source=source, columns=columns, width=800)

controls = widgetbox(slider1, slider2, button)
table = widgetbox(data_table)

layout = row(controls,table)
curdoc().add_root(layout)
curdoc().title = "Export CSV"

update()