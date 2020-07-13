import tkinter as tk

def show_output() :
    num = int(text_input.get())

    output = ''
    for i in range(1,13) :
        output += str(num) + 'x' + str(i) + ' = ' + str(num*i) + '\n'
    output_label.configure(text=output)



### create window
window = tk.Tk()
window.title('TITEL')
window.minsize(width=400, height=400)


### UI
titel_label = tk.Label(master=window, text='โปรแกรมสูตรคูณ')
titel_label.pack(pady=10)

text_input = tk.Entry(master=window, width=15)
text_input.pack()

ok_button = tk.Button(master=window, text='OK', width=15, height=2, command=show_output)
ok_button.pack(pady=10)

output_label = tk.Label(master=window)
output_label.pack(pady=10)


### show window
window.mainloop()

