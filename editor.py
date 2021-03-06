import gi
gi.require_version('Gtk', '3.0')
#gi.require_version('Granite', '1.0')
from gi.repository import Gtk,Gdk, Pango
import format_toolbar as ft

class Editor(Gtk.Grid):

	def __init__(self):

		Gtk.Grid.__init__(self,row_spacing=5, column_spacing=2)

		#scrolled window
		self.scrolled_window = Gtk.ScrolledWindow()
		self.scrolled_window.set_vexpand(True)
		self.scrolled_window.set_hexpand(True)
		
		#TextView
		self.textview = Gtk.TextView()
		self.textview.set_wrap_mode(3)
		self.textview.set_bottom_margin(5)
		self.textview.set_top_margin(5)
		self.textview.set_left_margin(5)
		self.textview.set_right_margin(5)
		self.textview.modify_font(Pango.FontDescription.from_string("11"))
		self.textbuffer = self.textview.get_buffer()
		self.serialized_format = self.textbuffer.register_serialize_tagset()
		self.deserialized_format = self.textbuffer.register_deserialize_tagset()

		#Scrolle Window to TextView
		self.scrolled_window.add(self.textview)

		self.tags = {}
		self.tags['bold'] = self.textbuffer.create_tag("bold",weight=Pango.Weight.BOLD)
		self.tags['italic'] = self.textbuffer.create_tag("italic",style=Pango.Style.ITALIC)
		self.tags['underline'] = self.textbuffer.create_tag("underline",underline=Pango.Underline.SINGLE)
		self.tags['ubuntu'] = self.textbuffer.create_tag("ubuntu", family = "Ubuntu Mono")
		self.tags['just_left'] = self.textbuffer.create_tag("just_left", justification=Gtk.Justification(0))
		self.tags['just_center'] = self.textbuffer.create_tag("just_center", justification=Gtk.Justification(2))
		self.tags['just_right'] = self.textbuffer.create_tag("just_right", justification=Gtk.Justification(1))
		self.tags['just_fill'] = self.textbuffer.create_tag("just_fill",justification=Gtk.Justification(3))
		self.tags['title'] = self.textbuffer.create_tag('title',font='25')
		self.tags['header'] = self.textbuffer.create_tag('header',font='18')

		#SIGNAL CONNECTIONS
		self.textbuffer.connect_after("insert-text",self.insert_with_tags)

		#TAGS
		self.tag_bar = Gtk.Entry()
		self.tag_bar.set_placeholder_text("Not Implemented")
		self.tag_bar.set_hexpand(True)


		#FORMAT TOOLBAR
		self.format_toolbar = ft.FormatBar()
		self.format_toolbar.bold.connect("clicked",self.toggle_tag, 'bold')
		self.format_toolbar.italic.connect("clicked",self.toggle_tag, 'italic')
		self.format_toolbar.underline.connect("clicked",self.toggle_tag, 'underline')
		self.format_toolbar.ubuntu.connect("clicked", self.toggle_tag,'ubuntu')
		self.format_toolbar.just_right.connect('clicked',self.apply_tag,'just_right')
		self.format_toolbar.just_left.connect('clicked',self.apply_tag,'just_left')
		self.format_toolbar.just_center.connect('clicked',self.apply_tag,'just_center')
		self.format_toolbar.just_fill.connect('clicked',self.apply_tag,'just_fill')
		self.format_toolbar.title.connect('clicked',self.apply_tag,'title')
		self.format_toolbar.header.connect('clicked',self.apply_tag,'header')

		self.attach(self.scrolled_window,0,0,2,1)
		self.attach(self.tag_bar,0,1,1,1)
		self.attach(self.format_toolbar,1,1,1,1)

	def get_text(self):

		return self.textbuffer.serialize(self.textbuffer,self.serialized_format,self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())

	def set_text(self,content):
		self.textbuffer.set_text("")
		if content != "":
			self.textbuffer.deserialize(self.textbuffer,self.deserialized_format,self.textbuffer.get_start_iter(),content)
		else:
			pass


	def toggle_tag(self,widget,tag):

		limits = self.textbuffer.get_selection_bounds()
		if len(limits) != 0:
			start,end = limits
			if self.format_toolbar.buttons[tag].get_active():
				self.textbuffer.apply_tag(self.tags[tag],start,end)
			else:
				self.textbuffer.remove_tag(self.tags[tag],start,end)

	def apply_tag(self,widget,tag):
		limits = self.textbuffer.get_selection_bounds()
		if len(limits) != 0:
			start,end = limits
			self.textbuffer.apply_tag(self.tags[tag],start,end)

	def get_clean_text(self):

		return self.textbuffer.get_text(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter(),False)

	def insert_with_tags(self,buffer,start_iter,data,data_len):

		#for some reason it fucks up the formatting when doing the initial deserialization
		#if we move back on a larger string
		#NOTE : Figure out what is happening
		if data_len == 1:
			start_iter.backward_char()
		end = self.textbuffer.props.cursor_position
		end_iter = self.textbuffer.get_iter_at_offset(end)
		for tag in self.format_toolbar.buttons:
			if self.format_toolbar.buttons[tag].get_active():
				self.textbuffer.apply_tag(self.tags[tag],start_iter,end_iter)