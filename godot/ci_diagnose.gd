extends SceneTree

func _initialize() -> void:
	var export := EditorExport.get_singleton()
	print("CI_DIAG: preset count=", export.get_export_presets().size())
	for preset in export.get_export_presets():
		var platform := preset.get_platform()
		print("CI_DIAG: preset=", preset.get_name(), " platform=", platform.get_name())
		print("CI_DIAG: can_export=", platform.can_export(preset, true))
		for option in platform.get_export_options():
			var key: String = option["name"]
			var warning: String = platform.get_option_warning(preset, key)
			if not warning.is_empty():
				print("CI_DIAG: option=", key, " warning=", warning)
	quit()
