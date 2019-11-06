import sys
import time
class ShowProcess():
    
    i = 0 
    max_steps = 0 
    max_arrow = 50 
    infoDone = 'done'

    def __init__(self, max_steps, infoDone = 'Done'):
        self.max_steps = max_steps
        self.i = 0
        self.infoDone = infoDone


    def show_process(self, present):
        self.i += 1
        #process_bar =  '[' + '>' * num_arrow + '-' * num_line + ']'\
                      #+ '%.2f' % percent + '%' + '\r'
        sys.stdout.write("processing %s [finish:%d/%d]\r" %(present,self.i,self.max_steps))
        #sys.stdout.write(process_bar) 
        sys.stdout.flush()
        if self.i >= self.max_steps:
            self.close()

    def close(self):
        print('')
        print(self.infoDone)
        self.i = 0
"""
if __name__=='__main__':
    max_steps = 100
    process_bar = ShowProcess(max_steps, 'OK')
    for i in range(max_steps):
        process_bar.show_process()
        time.sleep(0.02)
"""