set noswapfile
:syntax on
:set number
set mmp=5000

au filetype go inoremap <buffer> . .<C-x><C-o>

filetype plugin indent on
