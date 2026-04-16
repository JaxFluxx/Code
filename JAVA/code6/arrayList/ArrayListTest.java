package arrayList;

import java.util.*;

public class ArrayListTest
{
   public static void main(String[] args)
   {
      // fill the staff array list with three Employee objects
      ArrayList<Employee> staff = new ArrayList<>(100);

      staff.add(new Employee("Carl Cracker", 75000, 1987, 12, 15));
      staff.add(new Employee("Harry Hacker", 50000, 1989, 10, 1));
      staff.add(new Employee("Tony Tester", 40000, 1990, 3, 15));
      Employee e1=new Employee("李明",70000,1988,10,1);
      Employee e2=new Employee("张玮",50000,1995,8,1);
      staff.set(0,e1);
      staff.add(2,e2);
      staff.remove(e2);
      System.out.println(staff.size());  
      
      Employee[] staff1=new Employee[100];
      System.out.println(staff1.length ); 

      // raise everyone's salary by 5%
      for (Employee e : staff)
         e.raiseSalary(5);

      // print out information about all Employee objects
      for (Employee e : staff)
         System.out.println("name=" + e.getName() + ",salary=" + e.getSalary() + ",hireDay="
               + e.getHireDay());
      //创建一个数组，将列表中的元素拷贝到数组中
      Employee[] myStaff=new Employee[staff.size()];
      staff.toArray(myStaff);
      for(int i=0;i<myStaff.length;i++)
    	  System.out.println(myStaff[i].getName());
      
   }
}