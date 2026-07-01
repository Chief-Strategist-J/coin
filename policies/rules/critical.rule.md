- never assume anything at all 
- never add comments in code at all
- alway check memory and change log for references
- follow this folder structure /policies/rules/network_infrastructure_folder_structure.md
- for each time write test code for that please core+test
- commmited code must be revertable and cerry pickable
- maintain TLA+ specification
- for each feature/module/flow maintain contex.yml file you can take ref from this /policies/rules/context.file.creation.refs.yaml
- use existing library/module/or in existing code of package methods insted of writing code from scrach

- whenever de desided desisions we are making you have to kip update ascii tree accordingly desison tree in this file logs/change.log with time stamp and file name also do not explain in code just always add/update on point and follow consistancy in tree and if tree is going to biggger and bigger devide into short tree 

- example of change log

[timestamp] one line summery
└── File: file names and file path
    ├── Choice: 
    └── Changes:
        ├── feature-name-> changes
        └── affected files and what is affected

- whenever I say save this as memory that time you have to create add in last memory log same formate as change.log ascii tree update location logs/memory.log
