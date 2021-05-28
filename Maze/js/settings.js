class Settings {
    //----------------------------------------------------------
    // WebSocket
    
    static ws_protocol = 'ws://';
    static ws_host = 'localhost';
    static ws_port = 8765;

    //----------------------------------------------------------
    // World

    static noisy_moving = 0.9;  // 80% forward, 10% CW, 10% CCW
    static just_created = 'just_created';
    static is_going = 'is_going';
    static win = 'win';
    static lose = 'lose';

    //----------------------------------------------------------
    // Play field - Scene

    static scene_left = 30;
    static scene_width = 600;
    static scene_right = Settings.scene_width + Settings.scene_left;

    static scene_top = 100;
    static scene_height = 600;
    static scene_bottom = Settings.scene_height + Settings.scene_top;

    static cell_width = 50;
    static cell_height = 50;

    static chect_width = Math.floor(Settings.cell_width);// * 0.95);
    static chect_height = Math.floor(Settings.cell_height);// * 1.0);
}