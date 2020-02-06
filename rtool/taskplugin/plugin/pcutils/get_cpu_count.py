#coding=utf8

def get_cpu_count():                                                            
    import multiprocessing                                                      
    return multiprocessing.cpu_count()
