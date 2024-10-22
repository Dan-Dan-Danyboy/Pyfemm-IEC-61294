import femm
import os
from PIL import Image
from moviepy.editor import ImageSequenceClip
import shutil
import time
from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

femm_doc_path = os.path.join(os.getcwd(),'femm program','Geometry.FEC')

"""
Since the main .FEC document is originally in spanish the names of materials are asigned in spanish. These are the translations that need to be known:
Aceite -> Oil
Bola -> Sphere
Punta -> Spike
Aluminio -> Aluminum
Acero -> Steel
"""

class corona_type_PD:
    def __init__(self,V_sphere=80000,V_spike=0,FEC_doc=femm_doc_path):
        self.V_sphere = V_sphere
        self.V_spike = V_spike
        self.doc = FEC_doc
        self.modify_properties = self.mod_properties(self)
        self.make_vid = self.make_video(self)
        self.make_plots = self.make_plt(self)

    class mod_properties:
        def __init__(self,outer_instance):
            self.outer = outer_instance

        def oil_conductivity(self,ox=None,oy=None):
            if ox is None and oy is None:
                return ValueError('ox and oy cannot be both None')
            if oy is None:
                oy = ox
            elif ox is None:
                ox = oy
            femm.ci_modifymaterial('Aceite',1,ox)
            femm.ci_modifymaterial('Aceite',2,oy)

        def oil_relative_permitivity(self,ex=None,ey=None):
            if ey is None and ex is None:
                raise ValueError('ey and ex cannot be both None')
            if ey is None:
                ey = ex
            elif ex is None:
                ex = ey
            femm.ci_modifymaterial('Aceite',3,ex)
            femm.ci_modifymaterial('Aceite',4,ey)

        def steel_conductivity(self,ox,oy=None):
            if oy is None:
                oy = ox
            femm.ci_modifymaterial('Acero',1,ox)
            femm.ci_modifymaterial('Acero',2,ox)

        def aluminum_conductivity(self,ox,oy=None):
            if oy is None:
                oy = ox
            femm.ci_modifymaterial('Aluminio',1,ox)
            femm.ci_modifymaterial('Aluminio',2,ox)

        def sphere_tension(self,tension):
            femm.ci_modifyconductorprop("Bola",1,tension)

        def spike_tension(self,tension):
            femm.ci_modifyconductorprop("Punta",1,tension) 

    class make_video:
        def __init__(self,outer_instance):
            self.outer = outer_instance

        def execute_and_save(self,name,Imax=0.018,Vmax=80000):
                # femm.ci_saveas(name)
                femm.ci_analyse(3)
                femm.ci_loadsolution()
                # femm.ci_saveas(name)
                femm.co_showdensityplot(1,0,3,Imax,0)
                femm.co_zoom(2224.3,1050,2269,1154)
                self.save_adjusted_image('Current_density_images',name)
                femm.co_showdensityplot(1,0,0,Vmax,0)
                self.save_adjusted_image('Tension_distribution_images',name)

        def save_adjusted_image(self,folder,name,broad=200,narrow=450):
                bitmap_name = os.path.join(os.getcwd(),'Trash','trash.png')
                femm.co_savebitmap(bitmap_name)
                with Image.open(bitmap_name) as img:
                    cropped_im = img.crop((0,0,broad,narrow))
                    new_name= os.path.join(os.getcwd(),'Trash',folder,name+'.png')
                    cropped_im.save(new_name)
                os.remove(bitmap_name)

        def create_video_moviepy(self,image_folder, output_video_name, fps):
            # Get the list of image paths
            images = [os.path.join(image_folder, img) for img in sorted(os.listdir(image_folder)) if img.endswith(".png") or img.endswith(".jpg")]
            output_video = os.path.join(os.getcwd(),'Videos',output_video_name)
            
            # Check if images are present
            if not images:
                print("No images found in the provided folder.")
                return

            # Create a video clip from the image sequence
            clip = ImageSequenceClip(images, fps=fps)
            
            # Write the video to the output file
            clip.write_videofile(output_video, codec='libx264', fps=fps)
            print(f"Video saved as {output_video}")

        def tension_variation(self,v1=50000,v2=80000,step=1000,fps=4,erase_trash=True):
            try:
                os.makedirs(os.path.join(os.getcwd(),'Trash','Current_density_images'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')
            try:
                os.makedirs(os.path.join(os.getcwd(),'Trash','Tension_distribution_images'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')

            femm.openfemm()
            femm.opendocument(self.outer.doc)
            while v1<=v2:
                v1 += step
                # self.outer.modify_properties.sphere_tension(v1*1000)
                # self.outer.modify_properties.oil_conductivity(ox=1e-12, oy=1e-12) 
                self.outer.modify_properties.sphere_tension(v1)
                self.execute_and_save(str(v1),Vmax=v2)

            femm.closefemm()

            self.create_video_moviepy(os.path.join(os.getcwd(),'Trash','Current_density_images'),
                                      os.path.join(os.getcwd(),'Videos','Tension variation - current density.mp4'),fps)
            self.create_video_moviepy(os.path.join(os.getcwd(),'Trash','Tension_distribution_images'),
                                      os.path.join(os.getcwd(),'Videos','Tension variation - tension distribution.mp4'),fps)

            if erase_trash:
                try: 
                    shutil.rmtree(os.path.join(os.getcwd(),'Trash','Current_density_images'))
                except OSError:
                    pass
                try: 
                    shutil.rmtree(os.path.join(os.getcwd(),'Trash','Tension_distribution_images'))
                except OSError:
                    pass

        def conductivity_variation_oil(self,ox_1,ox_2,ox_step,oy=None,oy_step=None,fps=4,erase_trash=True):
            if oy is None:
                oy = ox_1
            if oy_step is None:
                oy_step = ox_step
            if ox_step <= 0:
                raise ValueError('Ox_step must be greater than 0')

            try:
                os.makedirs(os.path.join(os.getcwd(),'Trash','Current_density_images'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')
            try:
                os.makedirs(os.path.join(os.getcwd(),'Trash','Tension_distribution_images'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')
            
            femm.openfemm()
            femm.opendocument(self.outer.doc)

            while ox_1 <= ox_2:
                self.outer.modify_properties.oil_conductivity(ox_1,oy)
                self.execute_and_save(str(ox_1)+' - '+str(oy))

                ox_1 += ox_step
                oy += oy_step

            femm.closefemm()

            
            self.create_video_moviepy(os.path.join(os.getcwd(),'Trash','Current_density_images'),
                                      os.path.join(os.getcwd(),'Videos','Conductivity variation - current density.mp4'),fps)
            self.create_video_moviepy(os.path.join(os.getcwd(),'Trash','Tension_distribution_images'),
                                      os.path.join(os.getcwd(),'Videos','Conductivity variation - tension distribution.mp4'),fps)

            if erase_trash:
                try: 
                    shutil.rmtree(os.path.join(os.getcwd(),'Trash','Tension_distribution_images'))
                except OSError:
                    pass
                try: 
                    shutil.rmtree(os.path.join(os.getcwd(),'Trash','Current_density_images'))
                except OSError:
                    pass
            
    class make_plt:
        def __init__(self,outer_instance):
            self.outer = outer_instance
            self.intensity_variation = self.current_variation_with_properties_variation(self.outer)

        def calculate_current(self,x1=2228*100,x2=2268*100,y=1120):
            q = 0
            for x in range(x1,x2,100):
                x = x/100
                Jx,Jy = femm.co_getpointvalues(x,y)[1:3]
                J = ((abs(Jx))**2+(abs(Jy))**2)**(1/2)
                q += abs(J/100)
            return q
        
        def plot_formal_line(self,x, y, title, xlabel, ylabel, legend):
            try:
                os.makedirs(os.path.join(os.getcwd(),'Plots'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')           
            try:
                os.makedirs(os.path.join(os.getcwd(),'Plots','2D Plots'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')
                
            plt.figure(figsize=(8, 5))
            
            # Establecer el estilo formal
            plt.style.use('ggplot')
            
            # Fondo blanco
            plt.gcf().set_facecolor('white')
            
            # Gráfico de línea
            plt.plot(x, y, marker='o', linestyle='-', color='blue', label=legend, linewidth=2)

            # Títulos y etiquetas
            plt.title(title, fontsize=18, weight='bold')
            plt.xlabel(xlabel, fontsize=14)
            plt.ylabel(ylabel, fontsize=14)
            
            # Leyenda
            plt.legend(fontsize=12, loc='upper left')
            
            # Ejes y cuadrícula
            plt.grid(True, which='both', linestyle='--', linewidth=0.5)
            
            # Bordes de los ejes
            plt.gca().spines['top'].set_visible(False)
            plt.gca().spines['right'].set_visible(False)
            plt.gca().spines['left'].set_color('gray')
            plt.gca().spines['bottom'].set_color('gray')
            
            # Ajuste del diseño
            plt.tight_layout()
            
            # Guardar el gráfico
            plt.savefig(os.path.join(os.getcwd(),'Plots',title+' [{}-{}].png'.format(x[0],x[-1])), dpi=300)
            print('Plot saved in',os.path.join(os.getcwd(),'Plots',title+' [{}-{}].png'.format(x[0],x[-1])))
            
            # Mostrar el gráfico
            # plt.show()
        def plot_3d_surface(self, X, Y, Z, title='3D Surface Plot', xlabel='X Axis', ylabel='Y Axis', zlabel='Z Axis', cmap='viridis'):
            """
            Function to plot a 3D surface given X, Y, and Z values.
            
            Parameters:
            - X: 1D array for X coordinates
            - Y: 1D array for Y coordinates
            - Z: 2D array (list of lists) for Z values, corresponding to each X and Y point
            - title: Title of the plot (default: '3D Surface Plot')
            - xlabel: Label for the X axis (default: 'X Axis')
            - ylabel: Label for the Y axis (default: 'Y Axis')
            - zlabel: Label for the Z axis (default: 'Z Axis')
            - cmap: Colormap for surface plot (default: 'viridis')
            """
            try:
                os.makedirs(os.path.join(os.getcwd(),'Plots'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')           
            try:
                os.makedirs(os.path.join(os.getcwd(),'Plots','3D Plots'))
            except FileExistsError:
                pass
            except OSError:
                raise OSError('Operating System Error')
            
            # Convert X and Y to meshgrid (2D arrays) from 1D arrays
            X, Y = np.meshgrid(X, Y)
            
            # Convert Z to numpy array if it's not already
            Z = np.array(Z)
            
            # Create a figure for plotting
            fig = plt.figure(figsize=(10, 7))
            ax = fig.add_subplot(111, projection='3d')

            # Plot the surface
            surf = ax.plot_surface(X, Y, Z, cmap=cmap)

            # Add a color bar for the height values
            fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

            # Set labels and title
            ax.set_xlabel(xlabel)
            ax.set_ylabel(ylabel)
            ax.set_zlabel(zlabel)
            ax.set_title(title)

            plt.savefig(os.path.join(os.getcwd(),'Plots',title+' [{}-{}].png'.format(X[0],X[-1])), dpi=300)
            print('Plot saved in',os.path.join(os.getcwd(),'Plots',title+' [{}-{}].png'.format(X[0],X[-1])))
            # Show the plot
            # plt.show()

        def current_density_distribution_in_axis(self,num_dots=50,y1=0,y2=49.99):
            #(0,0) = (2247.5750,1125.8-50)
            #(0,50) = (2247.5750,1125.8)

            if y2>50:
                raise ValueError("Invalid value of y2. Cannot surpass 50")

            femm.openfemm()
            femm.opendocument(self.outer.doc)
            femm.ci_analyse(3)
            femm.ci_loadsolution()

            axis_analisis = np.arange(1125.8-0.95-y2,1125.8-0.95-y1,(y2-y1+0.000001)/num_dots)
            Voltage_values,Current_density_values = [],[]
            for y in axis_analisis:
                V,Jx,Jy = femm.co_getpointvalues(2247.5750,y)[:3]
                J = (abs(Jx)**2+abs(Jy)**2)**(1/2)
                Voltage_values.append(abs(V))
                Current_density_values.append(J)

            x_axis = np.arange(y1,y2,(y2-y1+0.000001)/num_dots)
            self.plot_formal_line(x_axis,Current_density_values,'Current density through axis','Height axis','Current density [A/mm^2]',None)
            self.plot_formal_line(x_axis,Voltage_values,'Tension values through axis','Height axis','Tension [V]',None)

        class current_variation_with_properties_variation:
            def __init__(self,outer_instance):
                self.outer = outer_instance

            def tension(self,value1,value2,num_dots):
                values = np.arange(value1,value2,(value2-value1)/num_dots)
                femm.openfemm()
                femm.opendocument(self.outer.doc)              
                Is = []
                for value in values:
                    self.outer.modify_properties.sphere_tension(value)
                    femm.ci_analyse(3)
                    femm.ci_loadsolution()
                    Is.append(self.outer.make_plots.calculate_current())
                self.outer.make_plots.plot_formal_line(values,Is,'Current variation caused by tension','Tension [V]','Current [A]',None)

            def conductivity(self,num_dots,ox1=None,ox2=None,oy1=None,oy2=None,x_equal_y=True):
                if ox1 is None:
                    if oy1 is None:
                        raise ValueError('ox and oy cannot be both None')
                    elif oy2 is None:
                        raise ValueError('Incomplete inputs')
                    else:
                        y_values = np.arange(oy1,oy2,(oy2-oy1)/num_dots)
                        if x_equal_y:
                            x_values = y_values
                        else:
                            x_values = [10**(-12) for value in y_values]
                elif ox2 is None:
                    raise ValueError('Incomplete inputs')
                else:
                    x_values = np.arange(ox1,ox2,(ox2-ox1)/num_dots)
                    if oy1 is None or oy2 is None:
                        if x_equal_y:
                            y_values = x_values
                        else:
                            y_values = [10**(-12) for value in x_values]
                    else:
                        y_values = np.arange(oy1,oy2,(oy2-oy1)/num_dots)
                
                femm.openfemm()
                femm.opendocument(self.outer.doc)
                
                if x_equal_y:
                    Is = []
                    for y_value in y_values:
                        self.outer.modify_properties.oil_conductivity(y_value,y_value)
                        femm.ci_analyse(3)
                        femm.ci_loadsolution()
                        Is.append(self.outer.make_plots.calculate_current())

                elif ox1 is None or ox2 is None:
                    Is = []
                    for y_value in y_values:
                        self.outer.modify_properties.oil_conductivity(x_values[0],y_value)
                        femm.ci_analyse(3)
                        femm.ci_loadsolution()
                        Is.append(self.outer.make_plots.calculate_current())
                
                elif oy1 is None or oy2 is None:
                    Is = []
                    for x_value in x_values:
                        self.outer.modify_properties.oil_conductivity(x_value,y_values[0])
                        femm.ci_analyse(3)
                        femm.ci_loadsolution()
                        Is.append(self.outer.make_plots.calculate_current())

                else:
                    Iss = []
                    for x_value in x_values:
                        Is = []
                        for y_value in y_values:
                            self.outer.modify_properties.oil_conductivity(x_value,y_value)
                            femm.ci_analyse(3)
                            femm.ci_loadsolution()
                            Is.append(self.outer.make_plots.calculate_current())
                        Iss.append(Is)

                if x_equal_y:
                    self.outer.make_plots.plot_formal_line(x_values,Is,'Current variation caused by conductivity variation',
                    'Conductivity [S/m]','Current [A]',None)
                elif ox1 is None or ox2 is None:
                    self.outer.make_plots.plot_formal_line(y_values,Is,'Current variation caused by conductivity variation in y axis',
                    'Conductivity [S/m]','Current [A]',None)          
                elif oy1 is None or oy2 is None:
                    self.outer.make_plots.plot_formal_line(x_values,Is,'Current variation caused by conductivity variation in x axis',
                    'Conductivity [S/m]','Current [A]',None)
                else:
                    self.outer.make_plots.plot_3d_surface(x_values,y_values,Iss,'Current variation caused by conductivity variation',
                    'Conductivity [S/m] x axis','Conductivity [S/m] y axis','Current [A]',None)
