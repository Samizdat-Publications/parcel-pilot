class_name TitleScreen
extends CanvasLayer
## Title card shown over the attract-mode flight.

var _best: Label


func _ready() -> void:
	layer = 10
	var root := UiKit.full_rect(Control.new())
	add_child(root)
	var box := VBoxContainer.new()
	box.set_anchors_and_offsets_preset(Control.PRESET_CENTER)
	box.grow_horizontal = Control.GROW_DIRECTION_BOTH
	box.grow_vertical = Control.GROW_DIRECTION_BOTH
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_theme_constant_override("separation", 12)
	root.add_child(box)
	box.add_child(UiKit.label("PARCEL PILOT", 120, UiKit.CREAM))
	box.add_child(UiKit.label("special delivery, by air", 36, UiKit.GOLD))
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, 60)
	box.add_child(spacer)
	box.add_child(UiKit.label("Press Space or Enter to start your shift", 40))
	_best = UiKit.label("", 30, UiKit.PAPER)
	box.add_child(_best)
	var help := UiKit.label("W/S climb and dive     A/D turn     Shift boost     Esc pause", 26, UiKit.PAPER)
	help.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	help.offset_bottom = -40
	help.grow_horizontal = Control.GROW_DIRECTION_BOTH
	help.grow_vertical = Control.GROW_DIRECTION_BEGIN
	root.add_child(help)
	visibility_changed.connect(_refresh)
	_refresh()


func _refresh() -> void:
	_best.text = "Best shift: %d" % Save.best_score if Save.best_score > 0 else ""
