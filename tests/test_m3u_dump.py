#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_m3u_dump
----------------------------------

Tests for `m3u_dump` module.
"""
import os

import pytest

from click.testing import CliRunner

from m3u_dump import cli
from m3u_dump.m3u_dump import M3uDump


@pytest.fixture(scope='session')
def music_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('music')


@pytest.fixture(scope='session')
def music_files(music_dir):
    d = music_dir
    d.join('dummy001.mp3').write('dummy')
    d.mkdir('sub').join('dummy002.mp3').write('dummy')
    d.mkdir('sub4').join('dummy002.mp3').write('dummy')
    d.mkdir('sub2').mkdir('sub3').join('あいう えお.mp3').write('dummy')
    d.mkdir('sub3').mkdir('かきく　けこ').join('あいう　えお.mp3').write('dummy')
    return d


# noinspection PyShadowingNames
@pytest.fixture(scope='session')
def multi_playlist_music_files(music_dir):
    d = music_dir
    d.join('aaaa.m3u').write('dummy')
    d.mkdir('sub7').join('multi-dummy001.mp3').write('dummy')
    d.mkdir('sub8').mkdir('sub2').join('multi-dummy002.mp3').write('dummy')
    d.mkdir('sub9').join('multi-あいう えお.mp3').write('dummy')
    d.mkdir('sub10').join('multi-あいう　えお.mp3').write('dummy')
    d.mkdir('sub11').join('multi-dummy004.mp3').write('dummy')
    d.mkdir('sub12').join('hello hello.mp3').write('dummy')
    return d


@pytest.fixture
def playlist_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('playlist')


# noinspection PyShadowingNames
@pytest.fixture
def playlist_current(playlist_dir):
    f = playlist_dir.join('playlist.m3u')
    f.write("""#EXTM3U
#EXTINF:409,artist - music_name
/full/path/dummy001.mp3
 #EXTINF:281,artist - music_name
/full/path/dummy002.mp3

#EXTINF:275,artist - music_name
music/あいう えお.mp3
#EXTINF:263,artist - music_name
/full/path/music/あいう　えお.mp3
 #EXTINF:288,artist - music_name
/full/path/aaa/dummy002.mp3
#EXTINF:222,artist = music_name
../../hello.mp3""")
    return f


@pytest.fixture(scope='session')
def already_exists_playlist(tmpdir_factory):
    d = tmpdir_factory.mktemp('already-dir')
    music_path = str(d.mkdir('music').join('already_path.mp3').write('dummy'))
    playlist_content = """#EXTM3U
#EXTINF:409,artist - music_name
{}""".format(os.path.join(str(d), 'music', 'already_path.mp3'))
    playlist_path = str(d.join('playlist.m3u').write(playlist_content))
    return d


# noinspection PyShadowingNames
@pytest.fixture
def playlist_current2(playlist_dir):
    f = playlist_dir.join('playlist2.m3u8')
    f.write("""#EXTM3U
#EXTINF:409,artist - music_name
/full/path/multi-dummy001.mp3
 #EXTINF:282,artist - music_name
/full/path/multi-dummy001.mp3
 #EXTINF:281,artist - music_name
/full/path/multi-dummy002.mp3

#EXTINF:275,artist - music_name
music/multi-あいう えお.mp3
#EXTINF:263,artist - music_name
/full/path/music/multi-あいう　えお.mp3
 #EXTINF:288,artist - music_name
/full/path/aaa/multi-dummy004.mp3
#EXTINF:222,artist = music_name
../../multi-hello.mp3""")
    return f


@pytest.fixture(scope='session')
def dump_music_path(tmpdir_factory):
    d = tmpdir_factory.mktemp('dst')
    return str(d)


def test_command_line_interface():
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 2  # must arguments
    assert 'Error: Missing argument' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help' in help_result.output
    assert 'Show this message and exit.' in help_result.output


# noinspection PyShadowingNames
def test_command_line_dryrun(playlist_current, tmpdir_factory, music_files):
    dst_dir = str(tmpdir_factory.mktemp('no-dump-music'))
    runner = CliRunner()
    result = runner.invoke(cli.main, ['--dry-run', str(playlist_current),
                                      dst_dir, '--fix-search-path',
                                      str(music_files)])
    assert 'Welcome m3u-dump' in result.output
    assert 'copy was completed(successful' in result.output
    assert result.exit_code == 0  # must arguments

    # copy できていないこと
    assert os.path.exists(os.path.join(dst_dir, 'dummy001.mp3')) is False
    assert os.path.exists(os.path.join(dst_dir, 'dummy002.mp3')) is False
    assert os.path.exists(os.path.join(dst_dir, 'あいう えお.mp3')) is False
    assert os.path.exists(os.path.join(dst_dir, 'あいう　えお.mp3')) is False
    assert os.path.exists(os.path.join(dst_dir, 'hello.mp3')) is False

    playlist_name = os.path.basename(str(playlist_current))
    playlist_path = os.path.join(dst_dir, playlist_name)
    assert os.path.exists(playlist_path) is False


# noinspection PyShadowingNames
def test_command_line_start(playlist_current, tmpdir_factory, music_files):
    dst_dir = str(tmpdir_factory.mktemp('dump-music'))
    runner = CliRunner()
    result = runner.invoke(cli.main, [str(playlist_current), dst_dir,
                                      '--fix-search-path', str(music_files)])
    for line in result.output.split('\n'):
        print(line)
    assert 'Welcome m3u-dump' in result.output
    assert 'copy was completed(successful' in result.output
    assert result.exit_code == 0  # must arguments

    # copy できているか確認する
    assert os.path.exists(os.path.join(dst_dir, 'dummy001.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'dummy002.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'あいう えお.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'あいう　えお.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'hello.mp3')) is False

    playlist_name = os.path.basename(str(playlist_current))
    playlist_path = os.path.join(dst_dir, playlist_name)
    assert os.path.exists(playlist_path) is True
    with open(playlist_path, 'r') as f:
        assert '#EXTM3U' == f.readline().rstrip('\n')
        assert '#EXTINF:409,artist - music_name' == f.readline().rstrip('\n')
        assert 'dummy001.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:281,artist - music_name' == f.readline().rstrip('\n')
        assert 'dummy002.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:275,artist - music_name' == f.readline().rstrip('\n')
        assert 'あいう えお.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:263,artist - music_name' == f.readline().rstrip('\n')
        assert 'あいう　えお.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:288,artist - music_name' == f.readline().rstrip('\n')
        assert 'dummy002.mp3' == f.readline().rstrip('\n')
        assert '' == f.readline().rstrip('\n')


# noinspection PyShadowingNames
def test_command_line_no_fix_start(playlist_current, tmpdir_factory, music_files):
    dst_dir = str(tmpdir_factory.mktemp('dump-music'))
    runner = CliRunner()
    result = runner.invoke(cli.main, [str(playlist_current), dst_dir])
    for line in result.output.split('\n'):
        print(line)
    assert 'Welcome m3u-dump' in result.output
    assert 'copy was completed(successful' in result.output
    assert result.exit_code == 0  # must arguments


# noinspection PyShadowingNames
def test_command_line_already_playlist(already_exists_playlist):
    music_path = os.path.join(str(already_exists_playlist), 'music')
    dst_dir = os.path.join(str(already_exists_playlist), 'dst')
    os.mkdir(dst_dir)
    playlist_path = os.path.join(str(already_exists_playlist), 'playlist.m3u')
    runner = CliRunner()
    result = runner.invoke(cli.main, [playlist_path, dst_dir,
                                      '--fix-search-path', str(music_path)])
    for line in result.output.split('\n'):
        print(line)
    assert 'Welcome m3u-dump' in result.output
    assert 'copy was completed(successful' in result.output
    assert result.exit_code == 0  # must arguments

    # copy できているか確認する
    assert os.path.exists(os.path.join(dst_dir, 'already_path.mp3')) is True

    playlist_path = os.path.join(dst_dir, 'playlist.m3u')
    assert os.path.exists(playlist_path) is True
    with open(playlist_path, 'r') as f:
        assert '#EXTM3U' == f.readline().rstrip('\n')
        assert '#EXTINF:409,artist - music_name' == f.readline().rstrip('\n')
        assert 'already_path.mp3' == f.readline().rstrip('\n')


# noinspection PyShadowingNames
def test_command_line_multi_playlist(playlist_current, playlist_current2,
                                     tmpdir_factory, music_files, multi_playlist_music_files):
    playlist_dir = os.path.dirname(str(playlist_current))
    dst_dir = str(tmpdir_factory.mktemp('dump-music'))
    runner = CliRunner()
    result = runner.invoke(cli.main, [playlist_dir, dst_dir,
                                      '--fix-search-path',
                                      str(music_files)])
    for line in result.output.split('\n'):
        print(line)
    assert 'Welcome m3u-dump' in result.output
    assert 'copy was completed(successful' in result.output
    assert result.exit_code == 0  # must arguments

    # copy できているか確認する
    assert os.path.exists(os.path.join(dst_dir, 'dummy001.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'dummy002.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'あいう えお.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'あいう　えお.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'hello.mp3')) is False

    assert os.path.exists(os.path.join(dst_dir, 'multi-dummy001.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'multi-dummy002.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'multi-あいう えお.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'multi-あいう　えお.mp3')) is True
    assert os.path.exists(os.path.join(dst_dir, 'multi-dummy004.mp3')) is True

    playlist_name = os.path.basename(str(playlist_current))
    playlist_path = os.path.join(dst_dir, playlist_name)
    assert os.path.exists(playlist_path) is True
    with open(playlist_path, 'r') as f:
        assert '#EXTM3U' == f.readline().rstrip('\n')
        assert '#EXTINF:409,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'dummy001.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:281,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'dummy002.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:275,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'あいう えお.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:263,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'あいう　えお.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:288,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'dummy002.mp3' == f.readline().rstrip('\n')
        assert '' == f.readline().rstrip('\n')

    playlist_name = os.path.basename(str(playlist_current2))
    playlist_path = os.path.join(dst_dir, playlist_name)
    assert os.path.exists(playlist_path) is True
    with open(playlist_path, 'r') as f:
        assert '#EXTM3U' == f.readline().rstrip('\n')
        assert '#EXTINF:409,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'multi-dummy001.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:282,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'multi-dummy001.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:281,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'multi-dummy002.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:275,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'multi-あいう えお.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:263,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'multi-あいう　えお.mp3' == f.readline().rstrip('\n')
        assert '#EXTINF:288,artist - music_name' == f.readline().rstrip(
            '\n')
        assert 'multi-dummy004.mp3' == f.readline().rstrip('\n')
        assert '' == f.readline().rstrip('\n')


# noinspection PyShadowingNames
def test_parse_playlist(playlist_current):
    playlist_path = str(playlist_current)
    files = list(M3uDump.parse_playlist(playlist_path))
    assert files[2] == '/full/path/dummy001.mp3'
    assert files[4] == '/full/path/dummy002.mp3'
    assert files[6] == 'music/あいう えお.mp3'
    assert files[8] == '/full/path/music/あいう　えお.mp3'
    assert len(files) == 13


# noinspection PyShadowingNames
def test_get_search_path_files(music_files):
    search_path_files = M3uDump.get_search_path_files(str(music_files))
    assert 'tmp/music0' in search_path_files['dummy001.mp3'][0]
    assert 'tmp/music0/sub' in search_path_files['dummy002.mp3'][0]
    assert 'tmp/music0/sub2/sub3' in search_path_files['あいう えお.mp3'][0]
    assert 'tmp/music0/sub3/かきく　けこ' in search_path_files['あいう　えお.mp3'][0]
    assert len(search_path_files.keys()) == 11


# noinspection PyShadowingNames
def test_fix_playlist(playlist_current, music_files):
    playlist_path = str(playlist_current)
    files = list(M3uDump.parse_playlist(playlist_path))

    search_path_files = M3uDump.get_search_path_files(str(music_files))

    p = M3uDump.fix_playlist(search_path_files, files)
    assert 'tmp/music0/dummy001.mp3' in p[2]
    assert 'tmp/music0/sub/dummy002.mp3' in p[4]
    assert 'tmp/music0/sub2/sub3/あいう えお.mp3' in p[6]
    assert 'tmp/music0/sub3/かきく　けこ/あいう　えお.mp3' in p[8]
    assert len(p) == 11


# noinspection PyShadowingNames
def test_copy_music_dryrun(playlist_current, music_files, dump_music_path):
    playlist_path = str(playlist_current)
    files = list(M3uDump.parse_playlist(playlist_path))

    search_path_files = M3uDump.get_search_path_files(str(music_files))

    playlist = M3uDump.fix_playlist(search_path_files, files)

    M3uDump.copy_music(playlist, dump_music_path, True)

    assert os.path.exists(
        os.path.join(dump_music_path, 'dummy001.mp3')) is False
    assert os.path.exists(
        os.path.join(dump_music_path, 'dummy002.mp3')) is False
    assert os.path.exists(os.path.join(dump_music_path, 'あいう えお.mp3')) is False
    assert os.path.exists(os.path.join(dump_music_path, 'あいう　えお.mp3')) is False


# noinspection PyShadowingNames
def test_copy_music_nodryrun(playlist_current, music_files, dump_music_path):
    playlist_path = str(playlist_current)
    files = list(M3uDump.parse_playlist(playlist_path))

    search_path_files = M3uDump.get_search_path_files(str(music_files))

    playlist = M3uDump.fix_playlist(search_path_files, files)

    M3uDump.copy_music(playlist, dump_music_path, False)

    assert os.path.exists(os.path.join(dump_music_path, 'dummy001.mp3'))
    assert os.path.exists(os.path.join(dump_music_path, 'dummy002.mp3'))
    assert os.path.exists(os.path.join(dump_music_path, 'あいう えお.mp3'))
    assert os.path.exists(os.path.join(dump_music_path, 'あいう　えお.mp3'))


# noinspection PyShadowingNames
def test_copy_music_override(playlist_current, music_files, dump_music_path):
    playlist_path = str(playlist_current)
    files = list(M3uDump.parse_playlist(playlist_path))

    search_path_files = M3uDump.get_search_path_files(str(music_files))

    playlist = M3uDump.fix_playlist(search_path_files, files)

    M3uDump.copy_music(playlist, dump_music_path, False)
    M3uDump.copy_music(playlist, dump_music_path, False)

    assert os.path.exists(os.path.join(dump_music_path, 'dummy001.mp3'))
    assert os.path.exists(os.path.join(dump_music_path, 'dummy002.mp3'))
    assert os.path.exists(os.path.join(dump_music_path, 'あいう えお.mp3'))
    assert os.path.exists(os.path.join(dump_music_path, 'あいう　えお.mp3'))


# noinspection PyShadowingNames
def test_load_from_playlist_path(playlist_dir, playlist_current2, playlist_current):
    playlist_path = str(playlist_dir)
    allowed_pattern = ['*.m3u', '*.m3u8']
    path_list = M3uDump.load_from_playlist_path(playlist_path, allowed_pattern)

    # os.walk は順序が分からない
    assert 'playlist.m3u' in path_list[0]
    assert 'playlist2.m3u8' in path_list[1]
    assert len(path_list) == 2
