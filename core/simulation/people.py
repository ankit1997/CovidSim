import pandas as pd

PEOPLE = pd.DataFrame({
	'person_id': [],                            # unique id of the person
	'home_region_name': [],                     # home region of the person (static)
	'region_name': [],                          # current region of the person
	'x': [],                                    # current x position of the person
	'y': [],                                    # current y position of the person
	'alive': [],                                # 0/1 if person is alive or not
	'infection': [],                            # degree of infection the person has [0, 1]
})