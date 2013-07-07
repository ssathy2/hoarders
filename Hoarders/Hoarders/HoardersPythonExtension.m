//
//  HoardersPythonExtension.m
//  Hoarders
//
//  Created by Sidd Sathyam on 6/30/13.
//  Copyright (c) 2013 Sidd Sathyam. All rights reserved.
//

#import "HoardersPythonExtension.h"

@implementation HoardersPythonExtension

+ (HoardersPythonExtension*) sharedPythonObject
{
	static HoardersPythonExtension* pyObject;
	static dispatch_once_t onceToken;
	dispatch_once(&onceToken, ^{
		pyObject = [[HoardersPythonExtension alloc] init];
	});
	return pyObject;
}

- (void) runDirChangeScriptWithPaths:(NSArray *)paths
{
	[self asyncRunScriptWithName: PYTHON_DIR_CHANGE_SCRIPT forPaths: paths];
}

- (void) runInitScript
{
	[self asyncRunScriptWithName: PYTHON_INIT_SCRIPT forPaths: nil];
}

- (NSData*) formatArrayForStdIn: (NSArray*) arr
{
	NSMutableData* data = [[NSMutableData alloc] init];
	
	for(NSURL* a in arr)
	{
		NSString* str = [NSString stringWithFormat: @"\"%@\"", [a relativePath]];
		[data appendBytes: [str UTF8String] length: [str length]];
		[data appendBytes: "\n" length: 1];
	}
	
	return data;
}

/*+ (void) runScriptWithName: (NSString*) name itemPaths: (NSArray*) paths;
{
	NSMutableString* output = [[NSMutableString alloc] init];
	//NSMutableString* error = [[NSMutableString alloc] init];
	//NSMutableData *data = [[NSMutableData alloc] init];
	
	NSTask* task = [[NSTask alloc] init];
    task.launchPath = @"/usr/bin/python";
	 
    NSString* scriptPath = [[NSBundle mainBundle] pathForResource: name ofType:@"py"];
	NSString* xmlPath = [[NSBundle mainBundle] pathForResource: HOARDERS_XML_DOC ofType: @"xml"];
    task.arguments = [NSArray arrayWithObjects: scriptPath, xmlPath, nil];
	
	NSPipe* stdInPipe = [NSPipe pipe];
	if(paths) {
		//[[stdInPipe fileHandleForWriting] writeData: [self formatArrayForStdIn: paths]];
		[task setStandardInput: stdInPipe];
	}
	else {
		// NSLog breaks if we don't do this...
		//[task setStandardInput: [NSPipe pipe]];
	}
	
    NSPipe *stdOutPipe = nil;
    stdOutPipe = [NSPipe pipe];
    [task setStandardOutput:stdOutPipe];
	
    NSPipe* stdErrPipe = nil;
    stdErrPipe = [NSPipe pipe];
    [task setStandardError: stdErrPipe];
	
	[task launch];
	NSData* data = [[NSData alloc] init];
	data = [self availableDataOrError: [stdOutPipe fileHandleForReading]];
	while (  [data length] > 0) {
		[output appendString:[[NSString alloc] initWithData:data encoding:NSUTF8StringEncoding]];
		data = [self availableDataOrError: [stdOutPipe fileHandleForReading]];
	}
	[[stdOutPipe fileHandleForReading] closeFile];
	
	NSLog(@"Blah task finished...%@", output);
}


//slightly modified version of Chris Suter's category function
//used as a private method
+ (NSData *) availableDataOrError: (NSFileHandle *)file {
	for (;;) {
		@try {
			return [file availableData];
		} @catch (NSException *e) {
			if ([[e name] isEqualToString:NSFileHandleOperationException]) {
				if ([[e reason] isEqualToString: @"*** -[NSConcreteFileHandle availableData]: Interrupted system call"]) {
					continue;
				}
				return nil;
			}
			@throw;
		}
	}
	
}*/

/*******************************************************
 *
 * MAIN ROUTINE
 *
 *******************************************************/

- (void)runScriptWithName:(NSString *)name forPaths:(NSArray *)paths
{
    //-------------------------------
    // Set up Task
    //-------------------------------
	NSTask* task = [[NSTask alloc] init];

	NSString* xmlPath = [[NSBundle mainBundle] pathForResource: HOARDERS_XML_DOC ofType: @"xml"];
    NSString* scriptPath = [[NSBundle mainBundle] pathForResource: name ofType:@"py"];

    [task setLaunchPath: @"/usr/bin/python"];
    [task setArguments: [NSArray arrayWithObjects: scriptPath, xmlPath, nil]];
	
	NSPipe* stdInPipe = [NSPipe pipe];
	
	[task setStandardInput: stdInPipe];
	
    [task setStandardOutput: [NSPipe pipe]];
    [task setStandardError: [task standardOutput]];
	
    [[NSNotificationCenter defaultCenter] removeObserver:self];
    [[NSNotificationCenter defaultCenter] addObserver:self
											 selector:@selector(commandSentData:)
												 name: NSFileHandleReadCompletionNotification
											   object: [[task standardOutput] fileHandleForReading]];

	
    [[NSNotificationCenter defaultCenter] addObserver:self
                    selector:@selector(taskTerminated:)
                        name:NSTaskDidTerminateNotification
                      object: task];
	
    [[[task standardOutput] fileHandleForReading] readInBackgroundAndNotify];
	
	[task launch];
	if (paths) {
		[[stdInPipe fileHandleForWriting] writeData: [self formatArrayForStdIn: paths]];
		[[stdInPipe fileHandleForWriting] closeFile];
	}
}

/*******************************************************
 *
 * OBSERVERS
 *
 *******************************************************/

- (void)commandSentData:(NSNotification*)n
{
    NSData* d;
    d = [[n userInfo] valueForKey:NSFileHandleNotificationDataItem];
	
    if ([d length])
    {
        NSString* s = [[NSString alloc] initWithData:d encoding:NSUTF8StringEncoding];
		
        NSLog(@"Received : %@",s);
    }
	
    [[n object] readInBackgroundAndNotify];
}

- (void)taskTerminated:(NSNotification*)n
{
    NSLog(@"Task terminated...");
}


- (void)asyncRunScriptWithName: (NSString*) name forPaths: (NSArray*) paths
{
	//dispatch_group_t group = dispatch_group_create();
    //dispatch_group_async(group, dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
		[self runScriptWithName: name forPaths: paths];
	//});
}


@end
