# -*- coding: utf-8 -*-
import fnmatch
import glob
import logging
import logging.config
import os
import pprint
import shutil

pp = pprint.PrettyPrinter(indent=4)

log = logging.getLogger(__name__)


class M3uDump:
    def __init__(self, args):
        self.args = args

        self.setup_logging()

        log.info('\n' + pp.pformat(self.args))

    @staticmethod
    def setup_logging():
        module_path = os.path.abspath(os.path.dirname(__file__))
        logging.config.fileConfig(os.path.join(module_path, 'logging.conf'))

    @staticmethod
    def parse_playlist(playlist_path):
        log.info('playlist{} reading....'.format(playlist_path))

        def is_not_empty_line(line):
            if len(line) > 0:
                return True
            else:
                return False

        with open(playlist_path, 'r') as f:
            return filter(is_not_empty_line, map(lambda x: x.strip(),
                                                 f.readlines()))

    @staticmethod
    def get_search_path_files(search_path):
        log.info('scanning search_path({0})...'.format(search_path))
        search_path_files = {}
        for (root, dirs, files) in os.walk(search_path):
            for f in files:
                if f in search_path_files:
                    search_path_files[f].append(root)
                else:
                    search_path_files.update({f: [root]})
        return search_path_files

    @staticmethod
    def is_comment(line):
        if line.lstrip().startswith('#EXTINF'):
            return True
        elif line.lstrip().startswith('#EXTM3U'):
            return True
        else:
            return False

    @staticmethod
    def fix_playlist(search_path_files, playlist_lines):
        new_playlist_lines = []

        for i in playlist_lines:
            if M3uDump.is_comment(i):
                new_playlist_lines.append(i)
                continue
            elif os.path.exists(i):
                new_playlist_lines.append(i)
                continue
            basename = os.path.basename(i)
            if basename in search_path_files:
                p = os.path.join(search_path_files[basename][0], basename)
                new_playlist_lines.append(p)
            else:
                log.warning(
                    'skip dump, because music file of {0} was '.format(
                        basename) +
                    'not found in search path.')
                # delete comment
                new_playlist_lines.pop()
        return new_playlist_lines

    @staticmethod
    def copy_music(playlist_lines, dump_music_path, dry_run):
        for i in playlist_lines:
            if M3uDump.is_comment(i):
                continue
            elif os.path.exists(i) is False:
                log.warning(
                    'skip copy, because music file({}) was not found.'.format(
                        i))
                continue

            dst = os.path.join(dump_music_path, os.path.basename(i))
            if dry_run is False:
                log.info('copying {0} -> {1}'.format(i, dst))
                shutil.copyfile(i, dst)
            else:
                log.info('(dryrun)copying {0} -> {1}'.format(i, dst))

    @staticmethod
    def save_playlist(playlist_name, playlist_lines, dump_music_path, dry_run):
        playlist_path = os.path.join(dump_music_path, playlist_name)
        if dry_run is False:
            with open(playlist_path, 'w') as f:
                log.info('writing playlist({})...'.format(playlist_path))
                for i in playlist_lines:
                    if M3uDump.is_comment(i):
                        f.write(i + '\n')
                    else:
                        music_file_name = os.path.basename(i)
                        f.write(music_file_name + '\n')
        else:
            log.info('(dryrun)writing playlist({})...'.format(playlist_path))

    def dump_playlist(self, playlist_path):
        playlist_lines = list(M3uDump.parse_playlist(playlist_path))
        log.debug('playlist_line is follows...')
        show_num = len(playlist_lines) if len(playlist_lines) < 3 else 3
        for i in range(0, show_num):
            log.debug(playlist_lines[i])

        # fix playlist
        if self.args['fix_search_path']:
            search_path_files = M3uDump.get_search_path_files(
                self.args['fix_search_path'])

            playlist_lines = M3uDump.fix_playlist(search_path_files,
                                                  playlist_lines)

        # copy music in playlist
        M3uDump.copy_music(playlist_lines, self.args['dump_music_path'],
                           self.args['dry_run'])

        # dump fixed playlist
        playlist_name = os.path.basename(playlist_path)
        M3uDump.save_playlist(playlist_name, playlist_lines,
                              self.args['dump_music_path'],
                              self.args['dry_run'])

    @staticmethod
    def load_from_playlist_path(load_m3u_path, pattern_list):
        """
        return playlist_path array in playlist directory
        :param pattern_list:
        :param load_m3u_path:
        :return:
        """
        log.info('loading playlist({})...'.format(load_m3u_path))
        log.info('allowed pattern is {}'.format(pattern_list))
        path_list = []
        for (root, dirs, files) in os.walk(load_m3u_path):
            for f in files:
                if any(map(lambda x: fnmatch.fnmatch(f, x), pattern_list)):
                    path_list.append(os.path.join(root, f))
        return sorted(path_list)

    def start(self):
        log.debug('start -----')

        load_m3u_path = self.args['load_m3u_path']
        if os.path.isfile(self.args['load_m3u_path']):
            load_m3u_path = [self.args['load_m3u_path']]
        else:
            load_m3u_path = M3uDump.load_from_playlist_path(
                self.args['load_m3u_path'], self.args['playlist_pattern_list'])

        log.info('playlist is {}'.format(load_m3u_path))
        for i in load_m3u_path:
            self.dump_playlist(i)
        log.info('copy done.')
