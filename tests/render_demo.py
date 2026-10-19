"""Render the actual PyQt widgets offscreen against fictional demo data."""
import os
from pathlib import Path
import sys
os.environ['QT_QPA_PLATFORM']='offscreen'
root=Path(__file__).resolve().parents[1]
os.chdir(root); sys.path.insert(0,str(root))
from PyQt5.QtWidgets import QApplication
import db
from windows import windows as ui
app=QApplication([])
from PyQt5.QtGui import QFontDatabase, QFont
if Path('C:/Windows/Fonts/arial.ttf').exists():
    QFontDatabase.addApplicationFont('C:/Windows/Fonts/arial.ttf')
    app.setFont(QFont('Arial',10))
out=root/'docs'/'screenshots'; out.mkdir(parents=True,exist_ok=True)
widgets=[]
auth=ui.Authorization(); widgets.append(('login',auth))
db.authenticate('demo','DemoPass2026'); ui.username='demo'
viewer=ui.UserMain('demo'); widgets.append(('viewer',viewer))
shows=db.searchPerformances()
purchase=ui.Reservation(shows[0]['id'],shows[0]['show_id']); widgets.append(('purchase',purchase))
reviews=ui.Reviews(shows[0]['id'],'Отзывы'); widgets.append(('reviews',reviews))
db.authenticate('admin','AdminPass2026'); ui.username='admin'
admin=ui.UserAdmin('admin'); widgets.append(('admin',admin))
add=ui.AddShow('admin'); widgets.append(('add-show',add))
registration=ui.Registration(); widgets.append(('registration',registration))
for name,widget in widgets:
    widget.show(); app.processEvents()
    assert widget.grab().save(str(out/(name+'.png')))
    widget.close()
print('Rendered',len(widgets),'actual application windows')
