(require 'pdj-utils)
(require 'pdj-venv)
(require 'pdj-python)
(require 'filenotify)

(defcustom toxic:test-env-dir (expand-file-name "~/.emacs-toxictest/")
  "Directory for the toxicbuild test environment.")

(defvar toxic:test-env-path toxic:test-env-dir)

(defcustom toxic:test-venv-name "toxicwebui"
  "Name of the virtualenv for the test environment.")

(defcustom toxic:original-venv-name "toxicwebui"
  "Name of the virutalenv for the acutal code")

(defcustom toxic:py-exec "/usr/bin/python3" "Python executable")

(defcustom toxic:py-venv-exec
  (concat "~/.virtualenvs/" toxic:test-venv-name "/bin/python")
  "Python executable for the test virtualenv")

(defcustom toxic:slave-buffer-name "toxicslave"
  "Toxicslave buffer's name")

(defcustom toxic:master-buffer-name "toxicmaster"
  "Toxicmaster buffer's name")

(defcustom toxic:poller-buffer-name "toxicpoller"
  "Toxicpoller buffer's name")

(defcustom toxic:secrets-buffer-name "toxicsecrets"
  "Toxicsecrets buffer's name")

(defcustom toxic:integrations-buffer-name "toxicintegrations"
  "Toxicbuild integrations buffer's name")

(defcustom toxic:notifications-buffer-name "toxicnotifications"
  "Toxicbuild notifications buffer's name")

(defcustom toxic:webui-buffer-name "toxicwebui"
  "Toxicweb ui buffer's name")

(defcustom toxic:run-all-tests-command
  "sh ./build-scripts/run_all_tests.sh --with-integrations"
  "The command used to run all tests in toxicubuild.")

(defcustom toxic:loglevel "debug"
  "Log level for toxicbuild servers")

(defvar toxic:bootstrap-buffer-name "toxic-bootstrap")


(defun toxic:run-all-tests ()
  "Runs tests using `pdj:test-command'. If test-args, concat it to
   the test command."

  (interactive)

  (defvar toxic--test-command)
  (if toxic:run-all-tests-command
      (let ((toxic--test-command toxic:run-all-tests-command))
	(pdj:compile-on-project-directory toxic--test-command))

    (message "No toxic:run-all-tests-command. You have to customize this.")))



(defun toxic:custom-keyboard-hooks ()
  "Custom key combinations for toxicbuild"

  (local-set-key (kbd "C-c t") 'toxic:run-all-tests))


(defun toxic:--run-in-env-on-test-dir (toxic-cmd buffer-name)
  (hack-local-variables)

  (let ((default-directory toxic:test-env-dir))
    (venv-workon toxic:original-venv-name)
    (setq toxic:--old-pypath (getenv "PYTHONPATH"))
    (setenv "PYTHONPATH" pdj:project-directory)
    (let ((pdj:multi-term-switch-to-buffer nil))
      (pdj:run-in-term toxic-cmd buffer-name))
    (setenv "PYTHONPATH" toxic:--old-pypath)
    (venv-workon toxic:original-venv-name)))

(defun toxic:--kill-buffer-shell-process (process-buffer-name)

  (defvar toxic:--process2kill nil)
  (defvar toxic:--buffer-name nil)

  (setq toxic:--buffer-name (concat "*" process-buffer-name "*"))
  (setq toxic:--process2kill (get-buffer-process toxic:--buffer-name))
  (kill-process toxic:--process2kill))


(defun toxic:--buffer-has-process (process-buffer-name)

  (defvar toxic:--buffer-name nil)

  (setq toxic:--buffer-name (concat "*" process-buffer-name "*"))
  (get-buffer-process toxic:--buffer-name))


(defun toxic:start-slave ()
  "Starts a slave instance in the test env"

  (interactive)

  (defvar toxic:--slave-path nil)
  (setq toxic:--slave-path (concat toxic:test-env-path "slave/"))
  (defvar toxic:--start-slave-cmd
    (format "toxicslave start %s --loglevel=%s"
	    toxic:--slave-path toxic:loglevel))

  (toxic:--run-in-env-on-test-dir
   toxic:--start-slave-cmd toxic:slave-buffer-name))


(defun toxic:stop-slave ()
  "Stops the slave test instance"

  (interactive)

  (toxic:--kill-buffer-shell-process toxic:slave-buffer-name))


(defun toxic:restart-slave ()
  "Restarts the slave test instance"

  (interactive)

  (deferred:$
    (deferred:next
      (lambda ()
	(toxic:stop-slave)))

    (deferred:nextc it
      (lambda ()
	(toxic:start-slave)))))


(defun toxic:start-master ()
  "Starts a master instance in the test env"

  (interactive)

  (defvar toxic:--master-path nil)
  (setq toxic:--master-path (concat toxic:test-env-path "master/"))
  (defvar toxic:--start-master-cmd
    (format "toxicmaster start %s --loglevel=%s"
	    toxic:--master-path toxic:loglevel))

  (defvar toxic:--master-buffer-name "toxicmaster")

  (toxic:--run-in-env-on-test-dir
   toxic:--start-master-cmd toxic:--master-buffer-name))


(defun toxic:stop-master ()
  "Stops the master test instance"

  (interactive)

  (toxic:--kill-buffer-shell-process toxic:--master-buffer-name))


(defun toxic:restart-master ()
  "Restarts the master test instance"

  (interactive)

  (deferred:$
    (deferred:next
      (lambda ()
	(toxic:stop-master)))

    (deferred:nextc it
      (lambda ()
	(toxic:start-master)))))


(defun toxic:start-notifications ()
  "Starts a toxicbuild notifications instance in the test env"

  (interactive)

  (defvar toxic:--notifications-path nil)
  (setq toxic:--notifications-path (concat toxic:test-env-path "notifications/"))
  (defvar toxic:--start-notifications-cmd
    (format "toxicnotifications start %s --loglevel=%s"
	    toxic:--notifications-path toxic:loglevel))

  (defvar toxic:--notifications-buffer-name "toxicnotifications")

  (toxic:--run-in-env-on-test-dir
   toxic:--start-notifications-cmd toxic:--notifications-buffer-name))


(defun toxic:stop-notifications ()
  "Stops the toxicnotifications test instance"

  (interactive)

  (toxic:--kill-buffer-shell-process toxic:--notifications-buffer-name))


(defun toxic:restart-notifications ()
  "Restarts the toxicnotifications test instance"

  (interactive)

  (deferred:$
    (deferred:next
      (lambda ()
	(toxic:stop-notifications)))

    (deferred:nextc it
      (lambda ()
	(toxic:start-notifications)))))


(defun toxic:start-integrations ()
  "Starts a toxicbuild integrations instance in the test env"

  (interactive)

  (defvar toxic:--integrations-path nil)
  (setq toxic:--integrations-path (concat toxic:test-env-path "integrations/"))
  (defvar toxic:--start-integrations-cmd
    (format "toxicintegrations start %s --loglevel=%s"
	    toxic:--integrations-path toxic:loglevel))

  (defvar toxic:--integrations-buffer-name "toxicintegrations")

  (toxic:--run-in-env-on-test-dir
   toxic:--start-integrations-cmd toxic:--integrations-buffer-name))


(defun toxic:stop-integrations ()
  "Stops the toxicbuild integrations test instance"

  (interactive)

  (toxic:--kill-buffer-shell-process toxic:--integrations-buffer-name))


(defun toxic:restart-integrations ()
  "Restarts the integrations test instance"

  (interactive)

  (deferred:$
    (deferred:next
      (lambda ()
	(toxic:stop-integrations)))

    (deferred:nextc it
      (lambda ()
	(toxic:start-integrations)))))


(defun toxic:start-poller ()
  "Starts a master's poller instance in the test env"

  (interactive)

  (defvar toxic:--poller-path nil)
  (setq toxic:--poller-path (concat toxic:test-env-path "poller/"))
  (defvar toxic:--start-poller-cmd
    (format "toxicpoller start %s --loglevel=%s"
	    toxic:--poller-path toxic:loglevel))

  (defvar toxic:--poller-buffer-name "toxicpoller")

  (toxic:--run-in-env-on-test-dir
   toxic:--start-poller-cmd toxic:--poller-buffer-name))


(defun toxic:stop-poller ()
  "Stops the poller test instance"

  (interactive)

  (toxic:--kill-buffer-shell-process toxic:--poller-buffer-name))


(defun toxic:restart-poller ()
  "Restarts the master' poller test instance"

  (interactive)

  (deferred:$
    (deferred:next
      (lambda ()
	(toxic:stop-poller)))

    (deferred:nextc it
      (lambda ()
	(toxic:start-poller)))))

(defun toxic:start-secrets ()
  "Starts a master's secrets instance in the test env"

  (interactive)

  (defvar toxic:--secrets-path nil)
  (setq toxic:--secrets-path (concat toxic:test-env-path "secrets/"))
  (defvar toxic:--start-secrets-cmd
    (format "toxicsecrets start %s --loglevel=%s"
	    toxic:--secrets-path toxic:loglevel))

  (defvar toxic:--secrets-buffer-name "toxicsecrets")

  (toxic:--run-in-env-on-test-dir
   toxic:--start-secrets-cmd toxic:--secrets-buffer-name))


(defun toxic:stop-secrets ()
  "Stops the secrets test instance"

  (interactive)

  (toxic:--kill-buffer-shell-process toxic:--secrets-buffer-name))


(defun toxic:restart-secrets ()
  "Restarts the master' secrets test instance"

  (interactive)

  (deferred:$
    (deferred:next
      (lambda ()
	(toxic:stop-secrets)))

    (deferred:nextc it
      (lambda ()
	(toxic:start-secrets)))))


(defun toxic:start-webui ()
  "Starts a web ui instance in the test env"

  (interactive)

  (hack-local-variables)

  (defvar toxic:--webui-path nil)
  (setq toxic:--webui-path (concat toxic:test-env-path "webui/"))

  (defvar toxic:--start-webui-cmd nil)
  (setq toxic:--start-webui-cmd
    (format "python ./toxicwebui/cmds.py start %s --loglevel=%s"
	    toxic:--webui-path toxic:loglevel))

  (defvar toxic:--webui-buffer-name "webui")
  (let ((pdj:multi-term-switch-to-buffer nil))
    (pdj:run-in-term toxic:--start-webui-cmd toxic:webui-buffer-name)))


(defun toxic:stop-webui ()
  "Stops the master test instance"

  (interactive)

  (toxic:--kill-buffer-shell-process toxic:webui-buffer-name))


(defun toxic:restart-webui ()
  "Restarts the webui test instance"

  (interactive)

  (deferred:$
    (deferred:next
      (lambda ()
	(toxic:stop-webui)))

    (deferred:nextc it
      (lambda ()
	(toxic:start-webui)))))


(defun toxic:start-all ()
  "Starts everything"

  (interactive)

  (toxic:start-slave)
  (toxic:start-poller)
  (toxic:start-secrets)
  (toxic:start-master)
  (toxic:start-integrations)
  (toxic:start-notifications)
  (toxic:start-webui))


(defun toxic:stop-all ()
  "Stops everything"

  (interactive)

  (toxic:stop-slave)
  (toxic:stop-poller)
  (toxic:stop-secrets)
  (toxic:stop-master)
  (toxic:stop-integrations)
  (toxic:stop-notifications)
  (toxic:stop-webui))


(defun toxic:restart-all ()
  "Restarts everything"

  (interactive)

  (toxic:restart-slave)
  (toxic:restart-master)
  (toxic:restart-poller)
  (toxic:restart-secrets)
  (toxic:restart-integrations)
  (toxic:restart-notifications)
  (toxic:restart-webui))


(defun toxic:fs-watcher (event)
  "Triggered by changes in toxicbuild files. Restarts servers."

  (defvar toxic:--event-file nil)
  (defvar toxic:--event-type nil)

  (setq toxic:--event-file (nth 2 event))
  (setq toxic:--event-type (nth 1 event))

  (if (eq toxic:--event-type 'changed)
      (if (string-match-p (regexp-quote "toxicwebui")
			  toxic:--event-file)
	  (toxic:restart-master))))


(defun toxic:add-watcher ()

  (hack-local-variables)

  (defvar toxic:--ui-path nil)
  (setq toxic:--ui-path (concat pdj:project-directory
				    "toxicwebui"))

  (file-notify-add-watch toxic:--ui-path '(change change)
			 'toxic:fs-watcher))


;; menu
(defun toxic:create-menu ()

  (interactive)

  (define-key-after global-map [menu-bar toxic-menu]
    (cons "ToxicDev" (make-sparse-keymap "ToxicDev")) 'Help)

  ;; Emacs menus are stupid. The order the items appear in the menu
  ;; is the oposite that they are declared here
  (define-key global-map [menu-bar toxic-menu toxic-restart-all]
    '(menu-item "Restart all" toxic:restart-all
		:visible (progn (and (toxic:--buffer-has-process
				      toxic:webui-buffer-name)
				     (toxic:--buffer-has-process
				      toxic:master-buffer-name)
				     (toxic:--buffer-has-process
				      toxic:slave-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-all]
    '(menu-item "Stop all" toxic:stop-all
		:visible (progn (and (toxic:--buffer-has-process
				      toxic:webui-buffer-name)
				     (toxic:--buffer-has-process
				      toxic:master-buffer-name)
				     (toxic:--buffer-has-process
				      toxic:slave-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-start-all]
    '(menu-item "Start all" toxic:start-all
		:visible (progn (and (not (toxic:--buffer-has-process
				      toxic:webui-buffer-name))
				(not (toxic:--buffer-has-process
				      toxic:master-buffer-name))
				(not (toxic:--buffer-has-process
				      toxic:slave-buffer-name))))))

  (define-key global-map [menu-bar toxic-menu toxic-fourth-separator]
    '(menu-item "--"))

  (define-key global-map [menu-bar toxic-menu toxic-restart-webui]
    '(menu-item "Restart toxicweb" toxic:restart-webui
		:visible (progn (toxic:--buffer-has-process
				 toxic:webui-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-webui]
    '(menu-item "Stop toxicweb" toxic:stop-webui
		:visible (progn (toxic:--buffer-has-process
				 toxic:webui-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-start-webui]
    '(menu-item "Start toxicweb" toxic:start-webui
		:visible (progn (not (toxic:--buffer-has-process
				      toxic:webui-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-integrations-separator]
    '(menu-item "--"))

  (define-key global-map [menu-bar toxic-menu toxic-restart-integrations]
    '(menu-item "Restart integrations" toxic:restart-integrations
		:visible (progn (toxic:--buffer-has-process
				 toxic:integrations-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-integrations]
    '(menu-item "Stop integrations" toxic:stop-integrations
		:visible (progn (toxic:--buffer-has-process
				 toxic:integrations-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-start-integrations]
    '(menu-item "Start integrations" toxic:start-integrations
		:visible (progn (not (toxic:--buffer-has-process
				      toxic:integrations-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-notifications-separator]
    '(menu-item "--"))

  (define-key global-map [menu-bar toxic-menu toxic-restart-notifications]
    '(menu-item "Restart notifications" toxic:restart-notifications
		:visible (progn (toxic:--buffer-has-process
				 toxic:notifications-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-notifications]
    '(menu-item "Stop notifications" toxic:stop-notifications
		:visible (progn (toxic:--buffer-has-process
				 toxic:notifications-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-start-notifications]
    '(menu-item "Start notifications" toxic:start-notifications
		:visible (progn (not (toxic:--buffer-has-process
				      toxic:notifications-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-third-separator]
    '(menu-item "--"))

  (define-key global-map [menu-bar toxic-menu toxic-restart-master]
    '(menu-item "Restart toxicmaster" toxic:restart-master
		:visible (progn (toxic:--buffer-has-process
				 toxic:master-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-master]
    '(menu-item "Stop toxicmaster" toxic:stop-master
		:visible (progn (toxic:--buffer-has-process
				 toxic:master-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-start-master]
    '(menu-item "Start toxicmaster" toxic:start-master
		:visible (progn (not (toxic:--buffer-has-process
				      toxic:master-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-second-minus-minus-separator]
    '(menu-item "--"))


  (define-key global-map [menu-bar toxic-menu toxic-restart-poller]
    '(menu-item "Restart toxicpoller" toxic:restart-poller
		:visible (progn (toxic:--buffer-has-process
				 toxic:poller-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-poller]
    '(menu-item "Stop toxicpoller" toxic:stop-poller
		:visible (progn (toxic:--buffer-has-process
				 toxic:poller-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-start-poller]
    '(menu-item "Start toxicpoller" toxic:start-poller
		:visible (progn (not (toxic:--buffer-has-process
				      toxic:poller-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-restart-secrets]
    '(menu-item "Restart toxicsecrets" toxic:restart-secrets
		:visible (progn (toxic:--buffer-has-process
				 toxic:secrets-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-secrets]
    '(menu-item "Stop toxicsecrets" toxic:stop-secrets
		:visible (progn (toxic:--buffer-has-process
				 toxic:secrets-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-start-secrets]
    '(menu-item "Start toxicsecrets" toxic:start-secrets
		:visible (progn (not (toxic:--buffer-has-process
				      toxic:secrets-buffer-name)))))

  (define-key global-map [menu-bar toxic-menu toxic-second-other-minus-minus-separator]
    '(menu-item "--"))

  (define-key global-map [menu-bar toxic-menu toxic-restart-slave]
    '(menu-item "Restart toxicslave" toxic:restart-slave
		:visible (progn (toxic:--buffer-has-process
				toxic:slave-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-stop-slave]
    '(menu-item "Stop toxicslave" toxic:stop-slave
		:visible (progn (toxic:--buffer-has-process
				toxic:slave-buffer-name))))

  (define-key global-map [menu-bar toxic-menu toxic-start-slave]
    '(menu-item "Start toxicslave" toxic:start-slave
		:visible (progn (not (toxic:--buffer-has-process
				     toxic:slave-buffer-name))))))


(defun toxic:setup ()

  (toxic:create-menu)
  (toxic:custom-keyboard-hooks)
  (toxic:add-watcher))


(when (string= (buffer-name) "pyproject.toml")
  (toxic:setup))

(add-hook 'python-mode-hook 'toxic:setup)
