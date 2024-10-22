from Corona_Type_PD import corona_type_PD

ctp = corona_type_PD()

# Example of creation of a video
ctp.make_vid.tension_variation(30000,60000,3000,3)

# Example of creation of a 2D plot
ctp.make_plots.current_density_distribution_in_axis() # Takes default values

# Example of creation of a 3D plot
ctp.make_plots.intensity_variation.conductivity(5,80,31,7,18,False)
