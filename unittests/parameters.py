# Solver parameter
solver = {
    'newton_iterations': '100',
    'iterations': '1000',
    'rayleighStiffness': '0',
    'rayleighMass': '0.1',
    'vdamping': '3', 
    'threshold': "0.000000001",
    'tolerance': "0.0000000001", 
}

# Parenchyma specificities
parenchyma = {
    'meshFile': './data/mesh/patient3_liver.stl',
    'material': 'SaintVenantKirchhoffMaterial',
    'young_modulus': 6500,
    'poissonRatio': 0.4,
    'n': [4 for i in range(3)],
    'bc_indices': "45 46 47 48 49 50 51 52 53 54 55 56",
    'totalMass': 1.5,
    'visualColor': 'blue'
}

# Vessels Mechanical coupling restshape parameters
RestShape = {
    'stiffness': "1000",
    'angularStiffness': '10'
}

# Vessels specificities
vessels = {
    'meshFile': "./data/mesh/processed_porteveine.stl",
    'skeleton_output': "./data/skeleton/output_skeleton.txt",
    'young_modulus': '0.62e5',
    'poissonRatio': '0.4',
    'radiusInner': '0.0029',
    'radius': '0.003',
    'totalMass': '0.1',
    'showAxisSizeFactor': '0.005',
    'visualColor': 'red',
    'sampling_rate': 0.005,
    'vesselsCoupling': RestShape,
}

# Mapping parameters
mapping = {
    'stiffness': " 1000 0 0 "
}

# Digital Twin parameters
digitaltwin = {
    'solver': solver,
    'parenchyma': parenchyma,
    'vessels': vessels,
    'mapping': mapping    
}