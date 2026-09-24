class_name UiKit
extends RefCounted
## The game's UI language: colors, fonts, panel and button styles, and one shared Theme.
## Fonts are system fonts (Bahnschrift on Windows, with fallbacks), so there are still
## no bundled font files.

const INK := Color("3a2c24")
const CREAM := Color("fff6e6")
const PAPER := Color("fbeed4")
const RED := Color("d9412f")
const TEAL := Color("2f9c95")
const GOLD := Color("ffc93d")
const SKY := Color("6fb7e9")
const NAVY := Color("2e3e5c")
const FONT_NAMES := ["Bahnschrift", "Segoe UI", "Arial Rounded MT Bold", "Arial", "Helvetica",
	"DejaVu Sans", "sans-serif"]

static var _fonts := {}
static var _theme: Theme


static func font(weight := 700) -> Font:
	if not _fonts.has(weight):
		var f := SystemFont.new()
		f.font_names = PackedStringArray(FONT_NAMES)
		f.font_weight = weight
		_fonts[weight] = f
	return _fonts[weight]


static func style(size: int, color := CREAM, outline := 10, outline_color := INK, weight := 700) -> LabelSettings:
	var s := LabelSettings.new()
	s.font = font(weight)
	s.font_size = size
	s.font_color = color
	s.outline_size = outline
	s.outline_color = outline_color
	return s


static func label(text: String, size: int, color := CREAM, align := HORIZONTAL_ALIGNMENT_CENTER,
		outline := -1, weight := 700) -> Label:
	var l := Label.new()
	l.text = text
	l.label_settings = style(size, color, maxi(4, size / 6) if outline < 0 else outline, INK, weight)
	l.horizontal_alignment = align
	l.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## Ink-on-paper text without an outline, for use inside paper panels.
static func ink(text: String, size: int, color := INK, align := HORIZONTAL_ALIGNMENT_CENTER, weight := 700) -> Label:
	return label(text, size, color, align, 0, weight)


static func box(bg := PAPER, border := INK, radius := 16, border_w := 3, shadow := true, pad := Vector2(18, 10)) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = bg
	sb.border_color = border
	sb.set_border_width_all(border_w)
	sb.set_corner_radius_all(radius)
	sb.content_margin_left = pad.x
	sb.content_margin_right = pad.x
	sb.content_margin_top = pad.y
	sb.content_margin_bottom = pad.y
	sb.anti_aliasing = true
	if shadow:
		sb.shadow_color = Color(INK, 0.35)
		sb.shadow_size = 6
		sb.shadow_offset = Vector2(0, 4)
	return sb


static func panel(bg := PAPER, radius := 16, pad := Vector2(18, 10)) -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", box(bg, INK, radius, 3, true, pad))
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p


static func pill(bg := Color(INK, 0.86)) -> PanelContainer:
	var p := PanelContainer.new()
	var sb := box(bg, Color(CREAM, 0.35), 999, 2, true, Vector2(26, 4))
	p.add_theme_stylebox_override("panel", sb)
	p.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return p


static func full_rect(control: Control) -> Control:
	control.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	control.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return control


static func format_clock(seconds: float) -> String:
	var s := maxi(0, ceili(seconds))
	return "%d:%02d" % [s / 60, s % 60]


## Pops a control in: scale overshoot from its center.
static func pop(control: Control, from := 0.6, seconds := 0.35) -> void:
	control.pivot_offset = control.size * 0.5
	control.scale = Vector2.ONE * from
	var tw := control.create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(control, "scale", Vector2.ONE, seconds)


static func theme() -> Theme:
	if _theme != null:
		return _theme
	var t := Theme.new()
	t.default_font = font(700)
	t.default_font_size = 28
	var pad := Vector2(26, 12)
	t.set_stylebox("normal", "Button", box(PAPER, INK, 14, 3, true, pad))
	t.set_stylebox("hover", "Button", box(GOLD, INK, 14, 3, true, pad))
	t.set_stylebox("pressed", "Button", box(Color("e8a93a"), INK, 14, 3, false, pad))
	t.set_stylebox("disabled", "Button", box(Color(PAPER, 0.5), Color(INK, 0.4), 14, 3, false, pad))
	var focus := box(Color(0, 0, 0, 0), RED, 16, 4, false)
	focus.draw_center = false
	focus.expand_margin_left = 5
	focus.expand_margin_right = 5
	focus.expand_margin_top = 5
	focus.expand_margin_bottom = 5
	t.set_stylebox("focus", "Button", focus)
	for c in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color"]:
		t.set_color(c, "Button", INK)
	t.set_color("font_color", "Label", INK)
	t.set_color("font_color", "CheckButton", INK)
	t.set_color("font_hover_color", "CheckButton", RED)
	t.set_color("font_focus_color", "CheckButton", RED)
	t.set_color("font_pressed_color", "CheckButton", INK)
	t.set_stylebox("focus", "CheckButton", focus)
	var track := box(Color(INK, 0.22), Color(INK, 0.0), 8, 0, false, Vector2(0, 5))
	t.set_stylebox("slider", "HSlider", track)
	t.set_stylebox("grabber_area", "HSlider", box(RED, INK, 8, 0, false, Vector2(0, 5)))
	t.set_stylebox("grabber_area_highlight", "HSlider", box(Color("e8604f"), INK, 8, 0, false, Vector2(0, 5)))
	t.set_stylebox("focus", "HSlider", focus)
	t.set_stylebox("panel", "PanelContainer", box())
	_theme = t
	return t
