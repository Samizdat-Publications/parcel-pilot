class_name UiKit
extends RefCounted
## Shared colors and label styles so every screen speaks the same visual language.

const INK := Color("3a2c24")
const CREAM := Color("fff6e6")
const PAPER := Color("fbeed4")
const RED := Color("d9412f")
const TEAL := Color("2f9c95")
const GOLD := Color("ffc93d")
const SKY := Color("6fb7e9")


static func style(size: int, color := CREAM, outline := 10, outline_color := INK) -> LabelSettings:
	var s := LabelSettings.new()
	s.font_size = size
	s.font_color = color
	s.outline_size = outline
	s.outline_color = outline_color
	s.shadow_size = 0
	return s


static func label(text: String, size: int, color := CREAM, align := HORIZONTAL_ALIGNMENT_CENTER) -> Label:
	var l := Label.new()
	l.text = text
	l.label_settings = style(size, color, maxi(4, size / 6))
	l.horizontal_alignment = align
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


static func full_rect(control: Control) -> Control:
	control.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	control.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return control


static func format_clock(seconds: float) -> String:
	var s := maxi(0, ceili(seconds))
	return "%d:%02d" % [s / 60, s % 60]
