module.exports = function (grunt) {

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-connect');
  grunt.loadNpmTasks('grunt-contrib-watch');
  grunt.loadNpmTasks('grunt-shell');

  grunt.initConfig({

    shell: {
      html: {
        command: 'make html'
      },
      publish: {
        command: 'make publish'
      }
    },

    watch: {
      files: ['content/**/*.md','theme/**/*.*'],
      tasks: ['build'],
      options: {
        livereload: 35729,
      }
    },

    copy: {
      main: {
        expand: true,
        cwd: 'theme/static/',
        src: ['**'],
        dest: 'output/static/',
      },
    },

    connect: {
      server: {
        options: {
          port: 8003,
          livereload: 35729,
          base: 'output',
          open: true,
          debug: false
        }
      }
    },

    clean: {
      build: {
        src: ["output/*"]
      }
    }

  });

  grunt.registerTask('build', ['clean', 'shell:html', ]);
  grunt.registerTask('serve', ['build', 'connect:server', 'watch']);
  grunt.registerTask('deploy', ['clean', 'shell:publish']);

};
