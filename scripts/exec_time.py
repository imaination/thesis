import datetime as dt

class Time:
    """Time stamp for code execution"""
    
    def get_current_time(self):
        now = dt.datetime.now()
        return(now)
    
    def get_start_time(self):
        # Start time
        start_time = self.get_current_time()
        return(start_time)
       
    def get_end_time(self):
        # End time
        end_time = self.get_current_time()
        elapsed_time = end_time - self.get_start_time()
        return(end_time, elapsed_time)
        
    def print_start(self):
        print('--------Start Script--------')
        print('--------Start Time: ' + self.get_start_time().strftime('%Y-%m-%d %H:%M:%S') + '-------\n')

    def print_end(self):
        print('Total ' + str(self.get_end_time()[1].seconds) + ' [sec]')
        print('-----End Time : ' + self.get_end_time()[0].strftime('%Y-%m-%d %H:%M:%S') + ' ---------')
        print('-----END SCRIPT------') 
