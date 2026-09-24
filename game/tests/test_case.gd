class_name TestCase
extends RefCounted
## Base class for unit tests run by tests/test_runner.tscn. Methods named test_* run
## in alphabetical file order; failed assertions are collected, never thrown.

var failures: PackedStringArray = []
var current_test := ""


func assert_true(condition: bool, message := "") -> void:
	if not condition:
		_fail("expected true" + _suffix(message))


func assert_false(condition: bool, message := "") -> void:
	if condition:
		_fail("expected false" + _suffix(message))


func assert_eq(actual: Variant, expected: Variant, message := "") -> void:
	var numeric := [TYPE_INT, TYPE_FLOAT]
	var comparable := typeof(actual) == typeof(expected) \
		or (typeof(actual) in numeric and typeof(expected) in numeric)
	if not comparable or actual != expected:
		_fail("expected %s, got %s%s" % [str(expected), str(actual), _suffix(message)])


func assert_near(actual: float, expected: float, epsilon := 0.001, message := "") -> void:
	if absf(actual - expected) > epsilon:
		_fail("expected %.4f +/- %.4f, got %.4f%s" % [expected, epsilon, actual, _suffix(message)])


func _fail(text: String) -> void:
	failures.append("%s: %s" % [current_test, text])


func _suffix(message: String) -> String:
	return "" if message.is_empty() else " (" + message + ")"
