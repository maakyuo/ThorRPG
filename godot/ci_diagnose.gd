extends SceneTree

func _initialize() -> void:
	var sdk: String = OS.get_environment("ANDROID_HOME")
	var java: String = OS.get_environment("JAVA_HOME")
	print("CI_DIAG: ANDROID_HOME=", sdk)
	print("CI_DIAG: JAVA_HOME=", java)
	for path in ["build-tools/34.0.0/aapt2", "build-tools/35.0.0/aapt2", "platforms/android-34/android.jar", "platforms/android-35/android.jar", "platform-tools/adb"]:
		print("CI_DIAG: ", path, " exists=", FileAccess.file_exists(sdk.path_join(path)))
	print("CI_DIAG: export templates installed=", DirAccess.dir_exists_absolute(OS.get_user_data_dir()))
	quit()
