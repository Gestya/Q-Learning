class World {
    constructor(scene) {
        LOGD('World::ctor');

        // Scene
        this.scene = scene;
        this.scene.setAttribute('style',
            `left:${Settings.scene_left}px; 
             top:${Settings.scene_top}px; 
             width:${Settings.scene_width}px; 
             height:${Settings.scene_height}px;`);

        // Chest
        let chect_img = document.getElementById('chest');
        chect_img.setAttribute('style', `width:${Settings.chect_width}px; height:${Settings.chect_height}px;`);
        let chect_div = document.getElementById('chest_div');
        //~~~this.chestCol = 10;
        this.chestRow = 1;
        this.chestCol = 4;
        this._putOver(this.chestRow, this.chestCol, chect_div)

        // Bot
        let bot_img = document.getElementById('bot');
        bot_img.setAttribute('style', `width:${Settings.cell_width}px; height:${Settings.cell_height}px;`);
        this.bot_div = document.getElementById('bot_div');

        // Maze
        // 0 - wall
        // 1 - grass
        // 2 - lava
        this.maze = [
            [0,0,0,0,0,0],
            [0,1,1,1,1,0],
            [0,1,0,0,1,2],
            [0,1,0,2,1,2],
            [0,1,0,0,1,2],
            [0,1,1,1,1,0],
            [0,0,0,0,0,0],
        ];

        this.state = Settings.just_created;

        this._drawMaze();

        var that = this;
        this.keyMap = [];
        this.keyMap.push( { keyCode: 'ArrowUp',    keyState: 0, action: function() {that._processAction('up'); }   } );
        this.keyMap.push( { keyCode: 'ArrowDown',  keyState: 0, action: function() {that._processAction('down');}  } );
        this.keyMap.push( { keyCode: 'ArrowLeft',  keyState: 0, action: function() {that._processAction('left');}  } );
        this.keyMap.push( { keyCode: 'ArrowRight', keyState: 0, action: function() {that._processAction('right');} } );


        this.clear();
    }

    clear() {
        // Keys
        this.keyUp = 0;
        this.keyLeft = 0;
        this.keyRight = 0;
        this.keyDown = 0;

        // Bot
        //~~~this.botRow = 11;
        //~~~this.botCol = 10;
        this.botRow = 5;
        this.botCol = 4;
    }

    start() {
        this.clear();
        this.update();
        this.state = Settings.is_going;
    }

    update() {
        this._putOver(this.botRow, this.botCol, this.bot_div);
    }

    get getWorldState() {
        let rows = this.maze.length;
        let cols = this.maze[0].length;
        return `{"world": {"height": ${rows}, "width": ${cols}, "row": ${this.botRow}, "col": ${this.botCol}, "state": "${this.state}"}}`;
    }

    onKey(event, state) {
        if (event.code == 'KeyR' && state != 0) {
            this.start();
        }

        this.keyMap.forEach( keyHandler => {
            if (event.code == keyHandler.keyCode) {
                if (state != 0 && keyHandler.keyState == 0) {
                    keyHandler.action();
                }
                keyHandler.keyState = state;
            }
        });
    }

    onMessaage(msg) {
        const obj = JSON.parse(msg);
        if (obj.action != null)
            this._processAction(obj.action);
        else if (obj.command != null)
            this._processCommand(obj.command);
        else
            LOGE(`Unsupported format: ${msg}`);
    }

    //----------------------------------------------------------
    // Internal

    _drawMaze() {
        for (let i = 0; i < this.maze.length; i++) {
            for (let j = 0; j < this.maze[i].length; j++) {
                let src = '?';
                switch (this.maze[i][j])
                {
                    case 0:
                        src = './img/stones.jpg';
                        break;
                    case 1:
                        src = './img/grass.jpg';
                        break;
                    case 2:
                        src = './img/lava.jpg';
                        break;
                }
                let id = i + '-' + j;
                this.scene.innerHTML += `<img id="${id}" src="${src}" width="${Settings.cell_width}" height="${Settings.cell_height}">`;
            }
            this.scene.innerHTML += '<br>';
        }
    }

    _putOver(row, col, obj) {
        let x = Settings.scene_left + Settings.cell_width  * col;
        let y = Settings.scene_top  + Settings.cell_height * row;
        obj.setAttribute('style', `left:${x}px; top:${y}px;`);
    }

    _processAction(action) {
        LOGD(`Action: ${action}`);

        //----------------------------------------
        // Update position
        let newPos = this._noisyMovement(action);
        let is_wall = this.maze[newPos.row][newPos.col] == 0
        if (!is_wall) {
            this.botRow = newPos.row;
            this.botCol = newPos.col;
            this.update();
        }

        //----------------------------------------
        // Reward AND state
        let reward = 0.0;
        let state = '';
        if (this.botRow == this.chestRow && this.botCol == this.chestCol) {
            // The game must be stopped!
            // WIN
            reward = 10;
            state = Settings.win;
        }
        else if (this.maze[this.botRow][this.botCol] == 2) {
            // The game must be stopped!
            // LOSE
            reward = -100;
            state = Settings.lose;
        }
        else {
            // Game is going
            reward = is_wall ? -0.5 : -0.1;
            state = Settings.is_going;
        }
        LOGD(`Reward: ${reward}`);
        LOGD(`State: ${state}`);

        let rsp = `{"response": {"row": ${this.botRow}, "col": ${this.botCol}, "reward": ${reward}, "state": "${state}"}}`;
        ws_send(rsp);
    }

    _processCommand(command) {
        LOGD(`Command: ${command}`);
        if (command == 'restart') {
            this.start();
            ws_send( this.getWorldState );
        }
    }

    _noisyMovement(action) {
        let col = this.botCol;
        let row = this.botRow;

        let dict = { 
            'left'  : 0,  // col--;
            'up'    : 1,  // row--;
            'right' : 2,  // col++;
            'down'  : 3,  // row++;
        };

        let movements = [ 
            () => {col--;},  // left
            () => {row--;},  // top
            () => {col++;},  // right
            () => {row++;}   // down
        ];

        let probability = Math.random();
        let index = dict[action];
        
        if (probability < noisy) {
            // Go forward
            movements[index]();
            LOGD(`Noisy movement: Go forward ${probability}`);
        }
        else if (probability >= 1.0 - (1.0 - noisy) / 2) {
            // Go CCW
            index = (index + 1) % movements.length;
            movements[index]();
            LOGD(`Noisy movement: Go CCW ${probability}`);
        }
        else {
            // Go CW
            index = (index - 1 + movements.length) % movements.length;
            movements[index]();
            LOGD(`Noisy movement: Go CW ${probability}`);
        }

        return {'col': col, 'row': row};
    }

}
