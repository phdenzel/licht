"""
licht.app

@author: phdenzel
"""
import os
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, Gdk, AppIndicator3
import licht
from licht.rest import LichtClient


class LichtIndicator(object):

    def __init__(self, root,
                 app_name='licht',
                 icon_path=None):
        self.app = root
        self.app_name = app_name
        if icon_path is not None:
            self.icon_path = icon_path
        else:
            self.icon_path = licht.icon_path
        self.icon_path = os.path.expanduser(self.icon_path)
        self.indicator = AppIndicator3.Indicator.new(
            self.app_name, self.icon_path,
            AppIndicator3.IndicatorCategory.OTHER
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        self.indicator.set_menu(self.generate_menu())

    def generate_menu(self):
        menu = Gtk.Menu()
        # get data once and store
        data = self.app.data
        if data.lights is not None:
            item = self.menu_item("Lights")
            submenu = self.lights_submenu(data.lights.names,
                                          device_id='lights/{}:{}')
            item.set_submenu(submenu)
            self.update_menu(submenu, data.lights)
            menu.append(item)
            menu.append(self.separator)
        if data.groups is not None:
            item = self.menu_item("Rooms")
            submenu = Gtk.Menu()
            for index, label in data.groups.names.items():
                # title_item = self.menu_item(label, bold=True)
                submenu.append(self.menu_item(label, bold=False))
                # submenu.append(self.menu_item('on', indent=1))
                # submenu.append(self.menu_item('dimm', indent=1))
                # submenu.append(self.separator)
            item.set_submenu(submenu)
            menu.append(item)
            menu.append(self.separator)
        if data.scenes is not None:
            item = self.menu_item("Scenes")
            submenu = Gtk.Menu()
            for index, label in data.scenes.names.items():
                # title_item = self.menu_item(label, bold=True)
                submenu.append(self.menu_item(label, bold=False))
                # submenu.append(self.menu_item('on', indent=1))
                # submenu.append(self.menu_item('dimm', indent=1))
                # submenu.append(self.separator)
            item.set_submenu(submenu)
            menu.append(item)
            menu.append(self.separator)

        item = Gtk.MenuItem()
        item.set_label("Exit")
        item.connect("activate", self.app.on_exit, '')
        menu.append(item)

        menu.show_all()
        return menu

    def lights_submenu(self, name_index, device_id='lights/{}:{}'):
        submenu = Gtk.Menu()
        for index, label in name_index.items():
            check_item = self.check_item(label, bold=True, indent=0,
                                         device_id=device_id.format(index, 'on'),
                                         connect=('toggled',
                                                  self.app.on_toggle_change))
            submenu.append(check_item)
            slider_item = self.slider_item(0, 100, 1, _type='%',
                                           device_id=device_id.format(index, 'bri'),
                                           connect=("value-changed",
                                                    self.app.on_scroll_change))
            submenu.append(slider_item)
            slider_item = self.slider_item(153, 500, 1, _type="Temp",
                                           device_id=device_id.format(index, 'ct'),
                                           connect=("value-changed",
                                                    self.app.on_scroll_change))
            submenu.append(slider_item)
            submenu.append(self.separator)
        return submenu

    def groups_submenu(self, name_index, device_id='groups/{}:{}'):
        pass

    def scenes_submenu(self, name_index):
        pass

    def update_menu(self, menu, data):
        for menu_item in menu.get_children():
            cls_name = menu_item.__class__.__name__
            if cls_name == 'SeparatorMenuItem':
                continue
            elif cls_name == 'CheckMenuItem':  # Title on/off
                device_id = menu_item.get_name()
                get_subpath, state_attr = device_id.split(':')
                idx = get_subpath.split('/')[-1]
                state = data[idx][data.state_cmd][state_attr]
                menu_item.set_active(state)
            elif cls_name == 'MenuItem':  # Scale
                device_id = menu_item.get_name()
                get_subpath, state_attr = device_id.split(':')
                idx = get_subpath.split('/')[-1]
                state = data[idx][data.state_cmd][state_attr]
                # TODO
                # convert state depending on state_attr
                slider = menu_item.get_children()[0]
                slider.set_value(state)
        # print(data)

    def menu_item(self, label, checkbox=False, indent=False, bold=False,
                  device_id=None, connect=None):
        menuitem = Gtk.MenuItem()
        if indent:
            for i in range(int(indent)):
                label = f"\t{label}"
        if label:
            menuitem.set_label(label)
            if bold:
                menuitem.get_children()[0].set_markup(f"<b>{label}</b>")
        if device_id:
            menuitem.set_name(device_id)
        if connect is not None:
            menuitem.connect(*connect)
        return menuitem

    def check_item(self, label, indent=False, bold=False, device_id=None,
                   connect=None):
        menuitem = Gtk.CheckMenuItem()
        if indent:
            for i in range(int(indent)):
                label = f"\t{label}"
        if label:
            menuitem.set_label(label)
            if bold:
                menuitem.get_children()[0].set_markup(f"<b>{label}</b>")
        if device_id:
            menuitem.set_name(device_id)
        if connect is not None:
            menuitem.connect(*connect)
        return menuitem

    def slider_item(self, range_min=0, range_max=100, range_inc=1,
                    device_id=None, _type='%', connect=None):
        slider_menu = self.menu_item('')
        slider = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL,
                                          range_min, range_max, range_inc)
        slider.set_hexpand(True)
        if connect is not None:
            slider.connect(*connect)
        if '%' in _type:
            slider.connect('format-value', self.slider_format(ps=_type))
        if "Temp" in _type:
            slider.connect('format-value', self.slider_format(title=_type))
        slider.set_value_pos(0)  # on the left
        if device_id:
            slider_menu.set_name(device_id)
            slider.set_name(device_id)
        slider_menu.add(slider)
        slider_menu.add_events(Gdk.EventMask.SCROLL_MASK)
        slider_menu.connect('scroll-event', self.app.on_scroll)
        return slider_menu

    def slider_format(self, title="", ps=""):
        def scale_formatter(widget, value, title=title, ps=ps):
            formatted_str = "{} {:3d}{} ".format(title, int(value), ps)
            return formatted_str
        return scale_formatter

    @property
    def separator(self):
        return Gtk.SeparatorMenuItem()


class LichtApplet(Gtk.Application):
    def __init__(self, app_name='licht', client=None):
        self.app_name = app_name
        self.client = client
        if self.client is None:
            self.client = LichtClient(licht.bridge_ip)
        self.indicator = LichtIndicator(self)

    @property
    def data(self):
        if hasattr(self, 'client'):
            return self.client.fetch_data()

    def on_scroll(self, widget, event, **kwargs):
        scale = widget.get_children()[0]
        current_val = scale.get_value()
        range_min = scale.get_adjustment().get_lower()
        range_max = scale.get_adjustment().get_upper()
        range_inc = scale.get_adjustment().get_step_increment()
        if event.direction == Gdk.ScrollDirection.UP:
            val = min(current_val+range_inc, range_max)
            print("Scrolled up")
        elif event.direction == Gdk.ScrollDirection.DOWN:
            val = max(current_val-range_inc, range_min)
            print("Scrolled down")
        scale.set_value(val)

    def on_toggle_change(self, widget, **kwargs):
        device_id = widget.get_name()
        get_subpath, state_attr = device_id.split(':')
        idx = get_subpath.split('/')[-1]
        print("Toggled")

    def on_scroll_change(self, widget, **kwargs):
        device_id = widget.get_name()
        get_subpath, state_attr = device_id.split(':')
        idx = get_subpath.split('/')[-1]
        print("Value Changed")
        # print(widget.get_value())
        # print(widget.get_name())

    def run(self):
        Gtk.main()

    def on_exit(self, widget, event):
        Gtk.main_quit()
