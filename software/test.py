

from SAMIControl import SAMIControl

robot = SAMIControl(
    arduino_port='COM6',
    baud_rate=115200,
    joint_config_file='Joint_config.json',
    behavior_folder='behaviors',
    emote_file='Emote.json',
    audio_folder='audio',
    starting_voice='Matt'
        )

robot.initialize_serial_connection()

robot.start_behavior("Wave.json")
robot.stop_behavior()


