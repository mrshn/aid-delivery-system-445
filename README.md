# Ceng 445 Project An Aid Delivery System

## About
During a disaster, people located in various locations of a wide area need various equipments
and materials. Also there are people that can provide those equipment and materials. In this
project a social platform where demanding and providing parties meet is being developed.
Each item request will work as a workflow. The demanding user adds a request based on
a geographic location on a hypotetical map. Other users will be able to query the requests
based on geographic area and item type. When they decided to send items of the request,
they respond it and enter an estimated time of arrival. Demanders will be able to see and
choose among the responses. When delivery is agreed, providers send items. When delivery
is completed, demander marks it as complete.
The users will be able to see the state of the program on a 2D grid immitating the map.
Also users will be able to register for the requests for specific items and geographic location,
and notified whenever a new request is available.

### Developers
 - Emre Şahin 2375731
 - Batuhan Tekmen 2380921


### Build and run the main
 - python3 main.py 
 - hostname and ports are optional you can specify them too
 - python3 main.py --host localhost --port 1423


## Semantic Commit Messages with Emojis
Commit format: `<emoji_type> <commit_type>(<scope>): <subject>. <issue_reference>`

### Example
```
:sparkles: feat(Component): Add a new feature. Closes: #
^--------^ ^--^ ^-------^   ^---------------^  ^------^
|          |    |           |                  |
|          |    |           |                  +--> (Optional) Issue reference: if the commit closes or fixes an issue
|          |    |           |
|          |    |           +---------------------> Commit summary
|          |    |
|          |    +---------------------------------> (Optional) Commit scope in the project
|          |
|          +--------------------------------------> Commit type: feat, fix, docs, refactor, test, style, chore, build, perf or ci
|
+-------------------------------------------------> (Optional) Emoji type. See: https://gitmoji.carloscuesta.me/
```

**The commit message will be:**

> feat: Add a new feature

**With optional features emoji, scope and issue reference:**

> :sparkles: feat(Component): Add a new feature. Closes: #..

### Commit Message Types

- **feat**: introducing a new feature to the codebase
- **fix**: fixing a bug in the codebase
- **docs**: adding or updating the documentation
- **refactor**: refactoring the production code
- **build**/**conf**: changes related to the build system (involving scripts, configurations) and package dependencies
- **test**: adding tests (no production code change)
- **ci**: changes related to the continuous integration and deployment system
- **style**: improving structure/format of the code e.g. missing semi colons (no production code change)
- **chore**: updating grunt tasks etc. (no production code change)
- **perf**: changes related to backward-compatible performance improvements

### Supported Emojis by Commit Message Types

| Type     | Emoji                                           |
| -------- | ----------------------------------------------- |
| feat     | :sparkles: `:sparkles:`                         |
| fix      | :bug: `:bug:`                                   |
| docs     | :memo: `:memo:`                                 |
| refactor | :recycle: `:recycle:`                           |
| build    | :construction_worker: `:construction_worker:`   |
| test     | :white_check_mark: `:white_check_mark:`         |
| ci       | :green_heart: `:green_heart:`                   |
| style    | :art: `:art:`                                   |
| chore    | :wrench: `:wrench:`                             |
| perf     | :zap: `:zap:`                                   |
