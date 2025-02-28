from globals import app

#App Rests
import RestProjects
import RestIoPorts
import RestStart

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


